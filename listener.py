# Necessary Libraries
import os
import time
import tempfile
import threading
from dotenv import load_dotenv
from datetime import datetime
from queue import Queue
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import signal
import warnings
from requests.exceptions import RequestsDependencyWarning

# Necessary Files
import config
from validation import validate_file
from send_email import send_error_email
from logger import listener_logger, log_separator
from Bulk_Invoice_Payment import call_process

warnings.simplefilter('ignore', RequestsDependencyWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)


temp_dir = tempfile.gettempdir() # Temporary directory for lock files
os.makedirs(temp_dir, exist_ok=True) # Ensure the temp_dir exists
credential_lock = threading.Lock() # Lock for thread safety
load_dotenv() # Load environment variables from .env file

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
file_queue = Queue()
credentials_lock = threading.Lock()  # Lock to handle credential access
USERS = config.credentials['worker_1'] # Users credentials for Snapsheet

LOCAL_DOWNLOADS = config.download_path
LOCAL_PROCESSED = config.completed_path
LOCAL_ERROR = config.error_path

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY
)


# Function to monitor S3 for new files
def monitor_files():
    listener_logger.info("Connecting to S3...")
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_UPLOADS_FOLDER)

        if 'Contents' in response:
            # Sort objects by LastModified date in descending order
            sorted_objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            files_picked = 0  # Counter to limit the number of files picked up

            for item in sorted_objects:
                if files_picked >= MAX_FILES_IN_PROCESSING:  # Only pick up to 2 files
                    listener_logger.info("Maximum limit of 2 files has been reached. Remaining files will be processed once the current files finish.")
                    break

                file_key = item['Key']
                if file_key.endswith('/'):
                    continue  # Skip folders

                # Check if it's an Excel file in the uploads folder
                if file_key.endswith('.xlsx') and file_key == S3_UPLOADS_FOLDER + '/' + os.path.basename(file_key):
                    listener_logger.info(f"Found Excel file: {file_key}")

                    # Validate the file
                    if validate_file(file_key):
                        file_queue.put(file_key)  # Add valid files to the queue
                        files_picked += 1  # Increment counter for files picked
                
            # Start processing the valid files using threading
            process_files_with_threads()

    except NoCredentialsError as e:
        listener_logger.error("Credentials not available.")
        send_error_email(e)
    except ClientError as e:
        listener_logger.error(f"An error occurred: {e}")
        send_error_email(e)

# Function to process files using multi-threading (max 2 at a time)
def process_files_with_threads():
    threads = []
    while not file_queue.empty():
        # Limit to 2 threads at a time
        if len(threads) < MAX_FILES_IN_PROCESSING:
            file_key = file_queue.get()  # Get the next file from the queue

            # Create a thread to process the file
            thread = threading.Thread(target=process_file_with_credential, args=(file_key,))
            thread.daemon = True  # Ensures threads exit when main program ends
            thread.start()
            threads.append(thread)
        else:
            listener_logger.info("Waiting for a thread to finish before processing the next file.")
            # Wait for the first thread to finish
            for thread in threads:
                thread.join()

            # Remove finished threads from the list
            threads = [thread for thread in threads if thread.is_alive()]

    # Ensure that all remaining threads are joined at the end
    for thread in threads:
        thread.join()

# Function to process file with an available credential
def process_file_with_credential(file_key):
    credential = None
    try:
        # Attempt to acquire a credential
        credential = acquire_unique_credential()
        if not credential:
            listener_logger.info(f"No available credentials for file: {file_key}. Re-queuing file.")
            file_queue.append(file_key)  # Re-queue the file for later processing
            return

        listener_logger.info(f"Acquired credentials: {credential['user']} for file {file_key}")
        download_path = os.path.join(LOCAL_DOWNLOADS, os.path.basename(file_key))
        os.makedirs(LOCAL_DOWNLOADS, exist_ok=True)

        listener_logger.info(f"Downloading {file_key}")
        s3.download_file(BUCKET_NAME, file_key, download_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(os.path.basename(file_key))
        filename = f"{name}_{timestamp}{ext}" 
        processing_key = os.path.join(S3_PROCESSING_FOLDER, filename)

        s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': file_key}, Key=processing_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)

        # Main Bulk Invoice Payment processing
        listener_logger.info(f"Processing file: {file_key}")
        completed_file = call_process(download_path, credential, filename)

        processed_key = os.path.join(S3_PROCESSED_FOLDER, completed_file)
        s3.upload_file(Filename=LOCAL_PROCESSED + "/" + str(completed_file), Bucket=BUCKET_NAME, Key=processed_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=processing_key)

        if os.path.exists(os.path.join(LOCAL_ERROR, completed_file)):
            error_key = os.path.join(S3_ERROR_FOLDER, completed_file)
            s3.upload_file(Filename=os.path.join(LOCAL_ERROR, completed_file), Bucket=BUCKET_NAME, Key=error_key)
            listener_logger.info(f"Error records stored in {error_key}")

        listener_logger.info(f"Completed processing: {file_key}")
        os.remove(download_path)

    except Exception as e:
        listener_logger.error(f"Failed to process {file_key}: {e}")
        if credential:
            filename = os.path.basename(file_key)
            error_key = os.path.join(S3_ERROR_FOLDER, filename)
            s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': file_key}, Key=error_key)
            os.remove(download_path)

    finally:
        if credential:
            release_credential(credential)

        # Mark the task as done
        file_queue.task_done()

# Function to acquire available credential
def acquire_unique_credential():
    with credential_lock:  # Ensure thread-safe access
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

# Cleanup stale locks during initialization
def cleanup_stale_locks():
    for user, _ in USERS:
        lock_file = os.path.join(temp_dir, f"{user}.lock")
        if os.path.exists(lock_file):
            os.remove(lock_file)

# Signal handler for safe termination
def handle_exit(signum, frame):
    listener_logger.info("Cleaning up before exit...")
    cleanup_stale_locks()
    exit(0)

# Register signal handlers for termination
signal.signal(signal.SIGINT, handle_exit)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # Termination signal

# Initialization
cleanup_stale_locks()

# Main function with multiprocessing
def main():
    signal.signal(signal.SIGINT, handle_exit)  # To Handle Ctrl+C
    while True:
        listener_logger.info("Starting a new run...")
        log_separator(listener_logger)
        monitor_files()
        listener_logger.info("Sleeping for 2 minutes before checking again...")
        listener_logger.info("Run completed.")
        log_separator(listener_logger)
        time.sleep(120)  # Check S3 every 2 minutes

if __name__ == '__main__':
    main()
