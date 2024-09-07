from fastapi import FastAPI, UploadFile, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import Product
from app.utils import validate_csv, extract_image_urls
from app.tasks import process_images

app = FastAPI()

@app.get("/health")
def root():
    return {"message": "Server is running...."}

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile, session: AsyncSession = Depends(get_session)):
    try:
        csv_data = await validate_csv(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Extract image URLs
    image_urls_by_product = extract_image_urls(csv_data)

    # Create a request ID and store data in DB
    request_id = str(uuid4())
    for product_name, image_urls in image_urls_by_product.items():
        new_product = Product(
            name=product_name,
            input_image_urls=','.join(image_urls),
            status="Pending"
        )
        session.add(new_product)
        await session.commit()

        # Start the asynchronous image processing task
        process_images.delay(new_product.id, image_urls)

    return {"request_id": request_id}

@app.get("/status/{request_id}")
async def get_status(request_id: str, session: AsyncSession = Depends(get_session)):
    product = await session.execute(
        session.query(Product).filter(Product.id == request_id)
    )
    product = product.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Request ID not found")

    return {"status": product.status}
