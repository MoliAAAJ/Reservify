from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from models.company import Company, CompanyResponse
from database import db, serialize_doc
from typing import List, Optional

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

collection = db["companies"]

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: Company):
    
    if collection.find_one({"name": company.name}):
        raise HTTPException(status_code=400, detail="El nombre del recurso ya existe")
    company_dict = company.dict()
    result = collection.insert_one(company_dict)
    created_company = collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_company)

@router.get("/", response_model=List[CompanyResponse])
def get_companies(
    skip: int = 0,
    limit: int = 10,
    id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7a")
):
    query = {}
    if id:
        query["_id"] = ObjectId(id)
    
    companies = collection.find(query).skip(skip).limit(limit)
    company_list = [serialize_doc(company) for company in companies]
    return company_list

