from fastapi import APIRouter, HTTPException, Query, status
from app.models.account_type import Account_type, Account_typeResponse, UpdateAccount_type
from app.database import db, serialize_doc
from bson.objectid import ObjectId
from typing import List, Optional

router = APIRouter(
  prefix="/account_types",
  tags=["Account_types"]
)

collection = db["account_types"]

@router.post("/", response_description="Tipo de cuenta creado", response_model=Account_typeResponse, status_code=status.HTTP_201_CREATED)
def create_account_type(account_type: Account_type):
  account_type_dict = account_type.dict()
  result = collection.insert_one(account_type_dict)
  created_account_type = collection.find_one({"_id": result.inserted_id})
  return serialize_doc(created_account_type)

@router.get("/", response_model=List[Account_typeResponse])
def get_account_types(skip: int = 0,
                      limit: int = 10,
                      user_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b")):
  query = {}
  if user_id:
    if not ObjectId.is_valid(user_id):
      raise HTTPException(status_code=400, detail="user_id inválido")
    query['user_id'] = ObjectId(user_id)
    
  account_types = collection.find(query).skip(skip).limit(limit)
  account_types_list = [serialize_doc(account_type) for account_type in account_types]
  return account_types_list

@router.get("/{account_type_id}", response_model=Account_typeResponse)
def get_account_type(account_type_id: str):
  if not ObjectId.is_valid(account_type_id):
    raise HTTPException(status_code=400, detail="ID inválido")
  account_type = collection.find_one({"_id": ObjectId(account_type_id)})
  if account_type:
    return serialize_doc(account_type)
  else:
    raise HTTPException(status_code=404, detail="Tipo de cuenta no encontrado")

@router.put("/{account_type_id}", response_model=Account_typeResponse)
def update_account_type(account_type_id: str, account_type: UpdateAccount_type):
  if not ObjectId.is_valid(account_type_id):
    raise HTTPException(status_code=400, detail="ID inválido")
  
  update_data = {k: v for k, v in account_type.dict().items() if v is not None}

  if not update_data:
    raise HTTPException(status_code=400, detail="No hay datos para actualizar")
  
  result = collection.update_one({"_id": ObjectId(account_type_id)}, {"$set": update_data})

  if result.matched_count == 0:
    raise HTTPException(status_code=404, detail="Tipo de cuenta no encontrada")
  
  updated_account_type = collection.find_one({"_id": ObjectId(account_type_id)})
  return serialize_doc(updated_account_type)

@router.delete("/{account_type_id}", response_model=dict)
def delete_account_type(account_type_id: str):
  if not ObjectId.is_valid(account_type_id):
    raise HTTPException(status_code=400, detail="ID inválido")

  result = collection.delete_one({"_id": ObjectId(account_type_id)})

  if result.deleted_count == 1:
    return {"detail": "Tipo de cuenta eliminado correctamente"}
  else:
    raise HTTPException(status_code=404, detail="Tipo de cuenta no encontrado")
