import hashlib
from datetime import datetime
import json
from bs4 import NavigableString
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageOps, ImageFont
import requests
from io import BytesIO
import os




def calc_start_time(run_log_file_path):
    start_datetime = datetime.now()
    start_time = start_datetime.replace(microsecond=0)
    log(run_log_file_path, f'Started scraping jobs at {start_time}\n')
    return(start_datetime)

def create_job_unique_code(job_details):
    list_str = ''.join(job_details)
    hash_code = hashlib.sha256(list_str.encode()).hexdigest()
    return hash_code

def log(file_path, data):
    # for the moment we are just printing the data, but in the future we can output logs to a file
    # write_to_txt(file_path, data)
    print(data)

def write_to_txt(file_path_in, data):
    with open(file_path_in, "a") as file:
        # Write some text to the file
        file.write(data)

def is_valid_json(content):
    try:
        json.loads(content)
    except ValueError as e:
        return False
    return True

def get_domain(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    # Parse the URL
    parsed_url = urlparse(url)
    # Get the network location part (netloc)
    netloc = parsed_url.netloc
    # Split the netloc by dots
    parts = netloc.split('.')
    # Retain the last two parts (domain and top-level domain)
    domain = '.'.join(parts[-2:])
    return domain

def save_image_to_file(image_data, filepath):
    # img = Image.open(BytesIO(image_data)).convert("RGBA")
    img = image_data
    img.save(filepath)

def convert_to_png(image_file):
    if 'jpeg' in image_file:
        jpeg_image = Image.open(image_file)
        png_file = os.path.splitext(image_file)[0] + '.png'
        jpeg_image.save(png_file)
        jpeg_image.close()
        os.remove(image_file)
        return(png_file)

def round_corners_image(image_data, radius):
    # Open image using Pillow (assuming image_data is already an Image object or loaded from BytesIO)
    img = image_data.convert("RGBA")  # Ensure image mode is RGBA for transparency support

    # Create a mask image with rounded corners
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)

    # Apply the mask to the image
    img_with_mask = Image.new("RGBA", img.size)
    img_with_mask.paste(img, (0, 0), mask)

    return img_with_mask


def make_image_square(image_data=None, local_file_name=None, output_size=128, background_color=(255, 255, 255, 0)):
    """
    Function to process logo image such that it is a perfect square and filled with a transparent background

    args
    background_color: the default is transparent
    """
    size = 250
    if local_file_name:
        img = Image.open(local_file_name).convert('RGBA')
    elif image_data:
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        
    try:
        # Determine the larger dimension (width or height)
        max_dimension = max(img.width, img.height)
        
        # Create a new square image with transparent background
        squared_img = Image.new('RGBA', (max_dimension, max_dimension), (0, 0, 0, 0))
        
        # Calculate position to paste the original image
        paste_position = ((max_dimension - img.width) // 2, (max_dimension - img.height) // 2)
        
        # Paste the original image onto the square canvas
        squared_img.paste(img, paste_position)
        
        # Resize the square image to the desired size
        resized_img = squared_img.resize((size, size), Image.LANCZOS)
        
        return(resized_img)

    except Exception as e:
        print(f"Error resizing image: {e}")






