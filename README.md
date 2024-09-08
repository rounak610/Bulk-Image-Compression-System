# Bulk-Image-Compression-System
This project is a web application built using Python. It uses FastAPI for the web server, PostgreSQL for storing data, and Celery for handling background tasks. 

### Setup

1. **Clone the Repository**

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/rounak610/Bulk-Image-Compression-System.git
cd Bulk-Image-Compression-System
```
2. **Create and Activate a Virtual Environment**
   
Create a Python virtual environment and activate it:
```bash
virtualenv myenv
source myenv/bin/activate
```

3. **Install Dependencies**

Install the required packages from requirements.txt:
```bash
pip install -r requirements.txt 
```

4. **Set up PostgreSQL**

Create a new PostgreSQL database and user:

```bash
sudo -u postgres psql

CREATE DATABASE image_processing;
CREATE USER myusername WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE image_processing TO myusername;
```
Update the DATABASE_URL in app/database.py with your PostgreSQL credentials.

5. **Create Database Tables**

Create the necessary tables in the database:
```bash
python3 -m app.create_tables
```

### Running the Application
1. **Start Redis**

Start the Redis server in a separate terminal:
```bash
redis-server
```

2. **Start Celery Worker**

Run the Celery worker to process background tasks:

```bash
celery -A app.tasks worker --loglevel=info
```

3. **Start the FastAPI Application**

Run the FastAPI app with Uvicorn:
```bash
uvicorn app.main:app --reload
```
The application will now be available at http://localhost:8000.

### API Endpoints
1. **Health Check**

Check if the server is running.
```bash
curl --location 'localhost:8000/health'
```

2. **Upload CSV**

Upload a CSV file containing product names and image URLs:.
```bash
curl --location 'localhost:8000/upload-csv/' \
--form 'file=@"/Users/rounakbhatia/Bulk-Image-Compression-System/sample.csv"'
```

3. **Get Status**

Check the status of image processing with the request ID:.
```bash
curl --location 'localhost:8000/status/c8c27581-2a81-448e-833c-3cd9fc45fe1e'
```
