from fastapi import FastAPI,  Request, Depends, HTTPException, status
from datetime import datetime
from zoneinfo import ZoneInfo
from models import Customer, Invoice
from db import create_all_tables
from .routers import customers, transactions, plans
import time
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated

app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(plans.router)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    print(f"Request: {request.url} - completed in {process_time:.4f} seconds")
    
    return response

security = HTTPBasic()

@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    print(credentials)

    if credentials.username == "juanevillam" and credentials.password == "123456":
        return {"message": f"Hello {credentials.username}"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}

@app.get("/time/{iso_code}")
async def get_time_by_iso_code(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = ZoneInfo(timezone_str)
    
    return {"time": datetime.now(tz)}

db_customers: list[Customer] = []

@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
