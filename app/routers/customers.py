from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select
from models import Customer, CustomerCreate, CustomerPlan, CustomerUpdate, Plan, StatusEnum
from db import SessionDep

router = APIRouter()

@router.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED, tags=["customers"])
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump()) 

    session.add(customer)
    session.commit()
    session.refresh(customer)
    
    return customer

@router.get("/customers/{customer_id}", response_model=Customer, tags=["customers"])
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    return customer_db

@router.patch("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED, tags=["customers"])
async def update_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer_db.sqlmodel_update(customer_data_dict)
    
    session.add(customer_db)
    session.commit()
    session.refresh(customer_db)
    
    return customer_db

@router.delete("/customers/{customer_id}", tags=["customers"])
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    session.delete(customer_db)
    session.commit()
    
    return {"message": "Customer deleted successfully"}

@router.get("/customers", response_model=list[Customer], tags=["customers"])
async def list_customers(session: SessionDep):
    return session.exec(select(Customer)).all()

@router.post("/customers/{customer_id}/plans/{plan_id}", tags=["customers"])
async def subscribe_customer_to_plan(customer_id: int, plan_id: int, session: SessionDep, plan_status: StatusEnum = Query()):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)
    
    if not customer_db or not plan_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer or plan not found")
    
    customer_plan_db = CustomerPlan(plan_id=plan_db.id, customer_id= customer_db.id, status=plan_status)
    
    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    
    return customer_plan_db

@router.get("/customers/{customer_id}/plans", tags=["customers"])
async def list_customer_plans(customer_id: int, session: SessionDep, plan_status: StatusEnum = Query()):
    customer_db = session.get(Customer, customer_id)
    
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    query = select(CustomerPlan).where(CustomerPlan.customer_id==customer_id).where(CustomerPlan.status==plan_status)
    plans = session.exec(query).all()

    return plans