import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import config
from send_email import send_text_email_invalid
from logger import listener_logger

# Load environment variables from .env file
load_dotenv()

# S3 and RDC Connection and Folder details
BUCKET_NAME = os.getenv("BUCKET_NAME")
ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

S3_UPLOADS_FOLDER = config.s3_uploads_folder
S3_INVALID_FOLDER = config.s3_invalid_folder


# Define your standard headers
STANDARD_HEADERS = ['Payee/Vendor', 'Client Claim Number', 'Invoice Number', 'Assignment Type', 'Adjuster Cost Category', 'Grand Total']

# Initialize the S3 client
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)


def validate_file(file_key):
    is_valid = True  # Flag to track validation status
    
    try:
        # Download the file object into memory
        file_obj = BytesIO()
        s3.download_fileobj(BUCKET_NAME, file_key, file_obj)
        file_obj.seek(0)  # Reset the file pointer to the beginning

        # Load the Excel file from the in-memory object
        excel_file = pd.ExcelFile(file_obj)

        # Handle cases with multiple sheets
        if len(excel_file.sheet_names) > 1:
            valid_sheet = None
            for sheet in excel_file.sheet_names:
                data = pd.read_excel(file_obj, sheet_name=sheet)
                # Check if the sheet contains any of the standard headers
                if any(header in data.columns for header in STANDARD_HEADERS):
                    valid_sheet = sheet
                    break
            if not valid_sheet:
                listener_logger.info("No sheet contains any of the required headers. File will not be processed.")
                is_valid = False
                move_file_to_invalid(file_key)
                send_text_email_invalid("Sagesure | RPA | Invalid File", f"No sheet contains any of the required headers. File {os.path.basename(file_key)} will not be processed.")
                return is_valid
            else:
                listener_logger.info(f"Validating the sheet: {valid_sheet}")
                data = pd.read_excel(file_obj, sheet_name=valid_sheet)
        else:
            # Single sheet case
            listener_logger.info(f"Single sheet detected: {excel_file.sheet_names[0]}")
            data = pd.read_excel(file_obj)

        # Check for missing headers
        missing_headers = set(STANDARD_HEADERS) - set(data.columns)
        if missing_headers:
            listener_logger.error(f"Missing headers: {missing_headers}")
            is_valid = False
            move_file_to_invalid(file_key)
            send_text_email_invalid("Sagesure | RPA | Invalid File", f"Missing headers: {missing_headers}.\nFile {os.path.basename(file_key)} will not be processed.")
            return is_valid

        listener_logger.info("Validation passed: The file has all required headers and is a valid .xlsx file.")
        return is_valid  # Return True if all validations pass

    except (FileNotFoundError, ValueError) as e:
        listener_logger.error(e)
        is_valid = False
        move_file_to_invalid(file_key)
        send_text_email_invalid("Sagesure | RPA | Invalid File", f"Error occurred while validating file: {e} \nFile {os.path.basename(file_key)} will not be processed.")
    except NoCredentialsError:
        listener_logger.error("Credentials not available.")
        is_valid = False
        move_file_to_invalid(file_key)
        send_text_email_invalid("Sagesure | RPA | Invalid File", f"Error occurred while validating file: {e} \nFile {os.path.basename(file_key)} will not be processed.")
    except ClientError as e:
        listener_logger.error(f"An error occurred: {e}")
        is_valid = False
        move_file_to_invalid(file_key)
        send_text_email_invalid("Sagesure | RPA | Invalid File", f"Error occurred while validating file: {e} \nFile {os.path.basename(file_key)} will not be processed.")


    return is_valid  # Return False if any validation fails

def move_file_to_invalid(file_key):
    copy_source = {'Bucket': BUCKET_NAME, 'Key': file_key}
    destination_key = f"{S3_INVALID_FOLDER}/{file_key.split('/')[-1]}"
    try:
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=copy_source, Key=destination_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        listener_logger.info(f"Moved {file_key} to {S3_INVALID_FOLDER} due to invalid format.")
    except ClientError as e:
        listener_logger.error(f"Failed to move file {file_key} to error folder: {e}")