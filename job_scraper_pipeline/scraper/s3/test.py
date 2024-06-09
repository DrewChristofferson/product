import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from ...utils.utils_parsing import get_url_content, get_element_text
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

def upload_html_to_s3(bucket_name, file_name, html_content):
    s3_client = boto3.client('s3')
    if html_content is None:
        print("HTML content is None. Unable to upload.")
        return
    else:
        print(html_content)
        # Upload the HTML content to S3
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=html_content, ContentType='text/html')


def download_file_from_s3(bucket_name, object_name, file_name=None):
    if file_name is None:
        file_name = object_name

    s3_client = boto3.client('s3')

    try:
        s3_client.download_file(bucket_name, object_name, file_name)
        print(f"File {object_name} from {bucket_name} downloaded as {file_name}")
    except FileNotFoundError:
        print(f"The file {file_name} was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")

def s3_test():
    # Usage
    file_name = 'job_scraper_pipeline/scraper/s3/test.txt'
    object_name = 'coinbase/random-id/raw-job-description.html'
    bucket_name = 'careersintech-job-postings'
    # current_path = os.getcwd()

    # Print the current working directory
    # print(f"The current working directory is: {current_path}")
    print(file_name, bucket_name, object_name)
    html_content_raw = get_url_content('https://www.coinbase.com/careers/positions/5479981?gh_jid=5479981&gh_src=20687b321us')
    html_content = str(html_content_raw)
    # text_content = get_element_text(html_content, 'div', 'Listing__DescriptionColumn-sc-aa86649f-7')
    # print(text_content)
    # upload_file_to_s3(file_name, bucket_name, object_name)
    # download_file_from_s3(bucket_name, object_name, file_name)

    upload_html_to_s3(bucket_name, object_name, html_content)

