import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
from ...utils.utils_parsing import get_url_content, get_element_text
from ..db_requests.update_job import update_job
import html2text


def upload_file_to_s3(file_name, bucket_name, object_name=None):
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the file
        response = s3_client.upload_file(file_name, bucket_name, object_name)
        print(f"File {file_name} uploaded to {bucket_name}/{object_name}")
    except FileNotFoundError:
        print(f"The file {file_name} was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")

def upload_txt_to_s3(company_name, job_id, content):
    s3_client = boto3.client('s3')
    bucket_name = 'careersintech-job-postings'
    object_name = f'{company_name}/{job_id}/raw-job-description.txt'
    if content is None:
        print("Content is None. Unable to upload.")
        return
    else:
        # Upload the HTML content to S3
        response = s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=content)



def download_file_from_s3(company_name, job_id):
    bucket_name = 'careersintech-job-postings'
    file_key = f'{company_name}/{job_id}/raw-job-description.txt'

    s3_client = boto3.client('s3')

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except FileNotFoundError:
        print(f"The file {file_key} was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")

# Function to upload PNG files to AWS S3
def upload_png_files_to_s3(directory_path, bucket_name):
    # Initialize S3 client
    s3 = boto3.client('s3')

    # List to store uploaded file URLs
    uploaded_urls = []

    try:
        # Loop through files in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith('.png'):
                file_path = os.path.join(directory_path, filename)
                s3_key = 'images' + '/' + filename

                # Upload file to S3 bucket
                s3.upload_file(file_path, bucket_name, s3_key)

                # Generate public URL for the uploaded file
                url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
                uploaded_urls.append(url)

                print(f"Uploaded {filename} to S3 bucket {bucket_name}")

        return uploaded_urls

    except NoCredentialsError:
        print("AWS credentials not available.")
        return None
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


