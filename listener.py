# Necessary Libraries
import os
import time
import logging
import tempfile
import threading
from datetime import datetime
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import signal
import warnings
from requests.exceptions import RequestsDependencyWarning

# Necessary Files
import config
from validation import validate_file
from Bulk_Invoice_Payment import call_process

warnings.simplefilter('ignore', RequestsDependencyWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)

# Set up logging with date and time format
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Temporary directory for lock files
temp_dir = tempfile.gettempdir()
os.makedirs(temp_dir, exist_ok=True) # Ensure the temp_dir exists

# Load environment variables from .env file
load_dotenv()

# S3 and RDC Connection and Folder details
BUCKET_NAME = os.getenv("BUCKET_NAME")
ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

S3_UPLOADS_FOLDER = config.s3_uploads_folder
S3_PROCESSING_FOLDER = config.s3_processing_folder
S3_PROCESSED_FOLDER = config.s3_processed_folder
S3_ERROR_FOLDER = config.s3_error_folder
S3_INVALID_FOLDER = config.s3_invalid_folder

MAX_FILES_IN_PROCESSING = 2  # Max simultaneous files to process
file_queue = []  # Array to store valid files to be processed
credentials_lock = threading.Lock()  # Lock to handle credential access
USERS = config.credentials['worker_2'] # Users credentials for Snapsheet
used_credentials = []  # List to track used credentials

LOCAL_DOWNLOADS = config.download_path
LOCAL_PROCESSED = config.completed_path
LOCAL_ERROR = config.error_path

'''
RDC_DOWNLOADS = config.download_path
RDC_PROCESSED = config.completed_path
RDC_ERROR = config.error_path
'''

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY
)

# Function to monitor S3 for new files
def monitor_files():
    print("\nConnecting to S3...")
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_UPLOADS_FOLDER)

        if 'Contents' in response:
            # Sort objects by LastModified date in descending order
            sorted_objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            for item in sorted_objects:
                file_key = item['Key']
                if file_key.endswith('/'):
                    continue  # Skip folders

                # Check if it's an Excel file in the uploads folder
                if file_key.endswith('.xlsx') and file_key == S3_UPLOADS_FOLDER + '/' + os.path.basename(file_key):
                    print(f"\nFound Excel file: {file_key}")

                    # Validate the file
                    if validate_file(file_key):
                        file_queue.append(file_key)  # Add valid files to the queue

            # Start processing the valid files using threading
            process_files_with_threads()

        else:
            print(f"No files found in the worker folder: {S3_UPLOADS_FOLDER}")

    except NoCredentialsError:
        print("Credentials not available.")
    except ClientError as e:
        print(f"An error occurred: {e}")

# Function to process files using multi-threading (max 2 at a time)
def process_files_with_threads():
    threads = []
    while file_queue:
        # Limit to 2 threads at a time
        if len(threads) < MAX_FILES_IN_PROCESSING:
            file_key = file_queue.pop(0)  # Pop the next file from the queue
            thread = threading.Thread(target=process_file_with_credential, args=(file_key,))
            thread.start()
            threads.append(thread)
        else:
            print("Waiting for a thread to finish before processing next file.")
            threads[0].join()  # Wait for the first thread to finish
            threads.pop(0)  # Remove the finished thread from the list

    # Wait for all threads to finish processing
    for thread in threads:
        thread.join()

# Function to process file with an available credential
def process_file_with_credential(file_key):
    # Acquire credential
    credential = acquire_unique_credential()
    if not credential:
        logger.info("No available credentials. Exiting task.")
        return

    logger.info(f"Acquired credentials: {credential['user']}")
    download_path = os.path.join(LOCAL_DOWNLOADS, os.path.basename(file_key))
    os.makedirs(LOCAL_DOWNLOADS, exist_ok=True)

    try:

        logger.info(f"Downloading {file_key}")
        s3.download_file(BUCKET_NAME, file_key, download_path)

        filename = os.path.basename(file_key)
        processing_key = os.path.join(S3_PROCESSING_FOLDER, filename)

        # Move the file to the processing folder in S3
        s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': file_key}, Key=processing_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)

        # Process the file
        logger.info(f"Processing file: {file_key}")
        completed_filename = call_process(download_path, credential)

        # # Generate a timestamped completed filename
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # name, ext = os.path.splitext(filename)
        # completed_filename = f"{name}_{timestamp}_completed{ext}"
        processed_key = os.path.join(S3_PROCESSED_FOLDER, completed_filename)
        print(f"Completed file: {completed_filename}")

        # Upload the completed file to the processed folder in S3
        s3.upload_file(Filename=LOCAL_PROCESSED + "/" + str(completed_filename), Bucket=BUCKET_NAME, Key=processed_key)        
        s3.delete_object(Bucket=BUCKET_NAME, Key=processing_key)
        
        # Check if there were any error records file generated - move to error files
        if os.path.exists(os.path.join(LOCAL_ERROR, completed_filename)):
            error_key = os.path.join(S3_ERROR_FOLDER, completed_filename)
            s3.upload_file(Filename=os.path.join(LOCAL_ERROR, completed_filename), Bucket=BUCKET_NAME, Key=error_key)
            logger.info(f"Error records stored in {error_key}")

        # Log completion and remove local file
        logger.info(f"Completed processing: {file_key}")
        os.remove(download_path)

    except Exception as e:
        logger.error(f"Failed to process {file_key}: {e}")
        # Move file to error folder in S3 in case of failure
        error_key = os.path.join(S3_ERROR_FOLDER, filename)
        s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': file_key}, Key=error_key)

    finally:
        # Release the credential
        release_credential(credential)

# Function to acquire available credential
def acquire_unique_credential():
    for user, password in USERS:
        lock_file = os.path.join(temp_dir, f"{user}.lock")
        if not os.path.exists(lock_file):
            with open(lock_file, 'w') as f:
                f.write("locked")
            return {'user': user, 'password': password}
    return None  # No available credentials

# Function to release credential
def release_credential(credential):
    lock_file = os.path.join(temp_dir, f"{credential['user']}.lock")
    if os.path.exists(lock_file):
        os.remove(lock_file)

# Graceful shutdown handler
def handle_exit(signum, frame):
    print("Received exit signal, terminating...")
    exit(0)

# Main function with multiprocessing
def main():
    signal.signal(signal.SIGINT, handle_exit)  # To Handle Ctrl+C
    while True:
        monitor_files()
        print("\nSleeping for 2 minutes before checking again...")
        time.sleep(120)  # Check S3 every 2 minutes

if __name__ == '__main__':
    main()
