from celery import Celery
from PIL import Image
import requests
from io import BytesIO
import os
import asyncio

celery_app = Celery('tasks')
celery_app.config_from_object('app.celeryconfig')

output_dir = os.path.join(os.path.expanduser("~"), "images")
os.makedirs(output_dir, exist_ok=True)

def compress_image(image_url):
    # Extract file extension from URL or content type
    file_extension = image_url.split('.')[-1] if '.' in image_url else 'jpg'
    file_extension = file_extension.lower()

    response = requests.get(image_url)
    if response.status_code != 200:
        raise ValueError(f"Failed to download image from URL: {image_url}")
    
    img = Image.open(BytesIO(response.content))
    img = img.convert("RGB")

    # Determine output format based on the extension
    if file_extension in ['jpg', 'jpeg']:
        output_format = 'JPEG'
    elif file_extension == 'png':
        output_format = 'PNG'
    else:
        output_format = 'JPEG'  # Default to JPEG if extension is unknown

    # Create output path
    file_name = os.path.basename(image_url.split('?')[0])
    compressed_image_path = os.path.join(output_dir, f"compressed_{file_name}")

    # Save the image
    img.save(compressed_image_path, format=output_format, quality=50)
    return compressed_image_path

@celery_app.task
def process_images(product_id, image_urls):
    output_urls = [compress_image(url) for url in image_urls]
    
    # Update the database with the output URLs
    from app.database import get_session
    from app.models import Product
    from sqlalchemy.future import select

    async def update_product():
        async for session in get_session():  # Changed to async for
            stmt = select(Product).filter(Product.id == product_id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            if product:
                product.output_image_urls = ','.join(output_urls)
                product.status = "Completed"
                await session.commit()

    # Run the async function in a thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_product())
    loop.close()
    
    return output_urls
