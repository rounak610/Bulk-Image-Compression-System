from fastapi import FastAPI, UploadFile, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session
from app.database import get_session
from app.models import Product
from app.utils import validate_csv, extract_image_urls
from app.tasks import process_images
from sqlalchemy.future import select

app = FastAPI()

@app.get("/health")
def root():
    return {"message": "Server is running...."}

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile, session: Session = Depends(get_session)):
    try:
        csv_data = await validate_csv(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    image_urls_by_product = extract_image_urls(csv_data)

    request_id = str(uuid4())
    for product_name, image_urls in image_urls_by_product.items():
        new_product = Product(
            name=product_name,
            input_image_url=','.join(image_urls),
            status="Pending",
            request_id=request_id
        )
        session.add(new_product)
        session.commit()

        process_images.delay(new_product.id, image_urls)

    return {"request_id": request_id}

@app.get("/status/{request_id}")
def get_status(request_id: str, session: Session = Depends(get_session)):
    result = session.execute(select(Product).filter(Product.request_id == request_id))
    products = result.scalars().all() 

    if not products:
        raise HTTPException(status_code=404, detail="Request ID not found")

    return [
        {"serial_number": product.id, "name": product.name, "status": product.status}
        for product in products
    ]
