import csv
from fastapi import UploadFile
from io import StringIO

async def validate_csv(file: UploadFile):
    content = await file.read()
    csv_reader = csv.reader(StringIO(content.decode("utf-8")))
    headers = next(csv_reader)
    expected_headers = ['S. No.', 'Product Name', 'Input Image Urls']
    if headers != expected_headers:
        raise ValueError("Invalid CSV format.")
    return list(csv_reader)

def extract_image_urls(csv_data):
    image_urls_by_product = {}
    for row in csv_data:
        serial_no, product_name, image_urls = row
        image_urls_by_product[product_name] = image_urls.split(',')
    return image_urls_by_product
