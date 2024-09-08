from celery import Celery
from PIL import Image
import requests
from io import BytesIO
import os
from app.database import get_session
from app.models import Product
from sqlalchemy.future import select
import csv
from webhook import call_webhook

celery_app = Celery('tasks')
celery_app.config_from_object('app.celeryconfig')

def create_output_dir(request_id):
    base_output_dir = os.path.join(os.path.dirname(__file__), "output_images")
    request_dir = os.path.join(base_output_dir, request_id)
    os.makedirs(request_dir, exist_ok=True)
    return request_dir

def compress_image(image_url, request_id):
    file_extension = image_url.split('.')[-1] if '.' in image_url else 'jpg'
    file_extension = file_extension.lower()

    response = requests.get(image_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to download image from URL: {image_url}")

    img = Image.open(BytesIO(response.content))
    img = img.convert("RGB")

    if file_extension in ['jpg', 'jpeg']:
        output_format = 'JPEG'
    elif file_extension == 'png':
        output_format = 'PNG'
    else:
        output_format = 'JPEG'

    request_dir = create_output_dir(request_id)
    file_name = os.path.basename(image_url.split('?')[0])
    compressed_image_path = os.path.join(request_dir, f"compressed_{file_name}")

    img.save(compressed_image_path, format=output_format, quality=50)
    return compressed_image_path

@celery_app.task
def process_images(product_id, image_urls):
    session = get_session()
    try:
        stmt = select(Product).filter(Product.id == product_id)
        result = session.execute(stmt)
        product = result.scalar_one_or_none()
        if product:
            output_urls = [compress_image(url, product.request_id) for url in image_urls]
            product.output_image_url = ','.join(output_urls)
            product.status = "Completed"
            session.commit()
            generate_output_csv(product)
            # now we can call a webhook after the task is completed
            # call_webhook(product.webhook_url, {"status": "Completed"})

    finally:
        session.close()

def generate_output_csv(product):
    output_csv_dir = os.path.join(os.path.dirname(__file__), "output_csv", product.request_id)
    os.makedirs(output_csv_dir, exist_ok=True)
    csv_file_path = os.path.join(output_csv_dir, "output.csv")

    session = get_session()
    try:
        stmt = select(Product).filter(Product.request_id == product.request_id)
        result = session.execute(stmt)
        products = result.scalars().all()

        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['S. No.', 'Product Name', 'Input Image Url', 'Output Image Url'])
            for idx, product in enumerate(products, start=1):
                writer.writerow([idx, product.name, product.input_image_url, product.output_image_url])
    finally:
        session.close()

    return csv_file_path