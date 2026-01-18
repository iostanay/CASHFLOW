# Customer Receipts API

FastAPI application for managing customer receipts with MySQL database connection.

## Features

- **POST /api/receipts** - Insert new customer receipt
- **GET /api/receipts** - List all customer receipts (with optional filtering)
- **GET /api/receipts/{id}** - Get specific receipt by ID

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database

The application is configured to connect to Railway MySQL database:
- Host: `maglev.proxy.rlwy.net`
- Port: `19323`
- Database: `cashflow_db`

Make sure the `customer_receipts` table exists in your database. The table structure should match the one provided in the SQL schema.

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Create Receipt

**POST** `/api/receipts`

Request body:
```json
{
  "customer_name": "John Doe",
  "receipt_nature": "Cash Inflow",
  "receipt_purpose": "Receipt from Customer",
  "receipt_date": "2024-01-15",
  "receipt_type": "Cash",
  "amount": 50000.00,
  "bank_name": "Bank of Example",
  "project_name": "Project ABC",
  "company_name": "Company XYZ",
  "remarks": "Payment for services"
}
```

### List Receipts

**GET** `/api/receipts`

Query parameters:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100)
- `customer_name` (optional): Filter by customer name (partial match)
- `receipt_type` (optional): Filter by receipt type (Cash, Cheque, Bank Transfer, UPI, Card)
- `start_date` (optional): Filter by start date (YYYY-MM-DD)
- `end_date` (optional): Filter by end date (YYYY-MM-DD)

Example:
```
GET /api/receipts?customer_name=John&receipt_type=Cash&limit=10
```

### Get Receipt by ID

**GET** `/api/receipts/{receipt_id}`

Example:
```
GET /api/receipts/1
```

## Receipt Types

- Cash
- Cheque
- Bank Transfer
- UPI
- Card

## Railway Deployment

### Deploy to Railway

1. **Install Railway CLI** (optional, or use Railway web dashboard):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy from GitHub**:
   - Push your code to GitHub
   - Go to [Railway Dashboard](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect FastAPI and run `pip install -r requirements.txt`

3. **Set Environment Variables** (if needed):
   - Go to your Railway project settings
   - Add `DATABASE_URL` environment variable if you want to use a different database
   - If using Railway's MySQL service, the `DATABASE_URL` will be automatically provided

4. **Build Configuration**:
   - Railway auto-detects FastAPI from `Procfile`
   - The `Procfile` specifies: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Railway will automatically set the `PORT` environment variable

5. **Deploy**:
   - Railway automatically builds and deploys on every push to main/master branch
   - Monitor logs in Railway dashboard

### Files for Railway Deployment

- `Procfile` - Specifies how to run the application
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version (optional, Railway auto-detects)
- `.railwayignore` - Files to ignore during build

### Troubleshooting

- If deployment fails, check Railway logs for errors
- Ensure `requirements.txt` is in the root directory
- Verify database connection string format in Railway environment variables
