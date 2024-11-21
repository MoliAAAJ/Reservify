from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import BaseModel
from app.database import db, serialize_doc
from bson.objectid import ObjectId
from typing import List, Optional
from passlib.context import CryptContext
from app.models.account import AccountResponse, ClientAccountResponse, CompanyAccountResponse, UpdateAccount, Account

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

class AccountLogin(BaseModel):
    username: str
    password: str

collection = db["accounts"]

# Configurar el contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return True #pwd_context.verify(plain_password, hashed_password)

@router.post("/login", response_model=AccountResponse)
async def login(account: AccountLogin):
    # Buscar el usuario en la base de datos
    db_account = collection.find_one({"username": account.username})
    
    if db_account is None or not verify_password(account.password, db_account["password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    return serialize_doc(db_account)

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: Account):
    # Verificar si el username o email ya existen
    if collection.find_one({"username": account.username}):
        raise HTTPException(status_code=400, detail="Username ya existe")
    if collection.find_one({"email": account.email}):
        raise HTTPException(status_code=400, detail="Email ya existe")
    
    account_dict = account.dict()
    # Hashear la contraseña antes de almacenarla
    account_dict["password"] = get_password_hash(account_dict["password"])
    result = collection.insert_one(account_dict)
    created_account = collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_account)

@router.get("/", response_model=List[AccountResponse])
def get_accounts(skip: int = 0, limit: int = 10, id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b")):
    
    if not id:
        accounts = collection.find().skip(skip).limit(limit)
        return [serialize_doc(account) for account in accounts]

    query = {"_id": ObjectId(id)}
    accounts = collection.find(query).skip(skip).limit(limit)
    return [serialize_doc(account) for account in accounts]
    

@router.get("/clients/{account_id}", response_model=ClientAccountResponse)
def get_client(account_id: str):
    account = get_account(account_id)
    type: str = account["account_type"]
    if type.lower() != "client":
        raise HTTPException(status_code=400, detail="Not a Client")
    client = {
        "id": account["id"],
        "name": account["name"],
        "email": account["email"]
    }
    return client

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: str):
    if not ObjectId.is_valid(account_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    account = collection.find_one({"_id": ObjectId(account_id)})
    if account:
        return serialize_doc(account)
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
@router.get("/companies/", response_model=List[CompanyAccountResponse])
def get_companies(skip: int = 0, limit: int = 10, id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b")):     
    accounts = get_accounts(skip, limit, id)
    companies = []
    for account in accounts:
        type: str = account["account_type"]
        if type.lower() != "company":
            continue
        company = {
            "id": account["id"],
            "name": account["name"],
            "email": account["email"],
            "thumbnailUrl": account["thumbnailUrl"]
        }
        companies.append(company)
        
    if companies.__len__() == 0:
        raise HTTPException(status_code=400, detail="No companies found")
    return companies
        

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: str, account: UpdateAccount):
    if not ObjectId.is_valid(account_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in account.dict().items() if v is not None}
    
    if 'password' in update_data:
        # Hashear la nueva contraseña
        update_data['password'] = get_password_hash(update_data['password'])
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = collection.update_one({"_id": ObjectId(account_id)}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    updated_account = collection.find_one({"_id": ObjectId(account_id)})
    return serialize_doc(updated_account)

@router.delete("/{account_id}", response_model=dict)
def delete_account(account_id: str):
    if not ObjectId.is_valid(account_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = collection.delete_one({"_id": ObjectId(account_id)})
    
    if result.deleted_count == 1:
        return {"detail": "Usuario eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
