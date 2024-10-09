from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from models.user import User, UserResponse, UpdateUser
from database import db, serialize_doc
from bson.objectid import ObjectId
from typing import List
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

class UserLogin(BaseModel):
    username: str
    password: str

collection = db["users"]

# Configurar el contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return True #pwd_context.verify(plain_password, hashed_password)

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):
    # Buscar el usuario en la base de datos
    db_user = collection.find_one({"username": user.username})
    
    if db_user is None or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    return serialize_doc(db_user)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    # Verificar si el username o email ya existen
    if collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username ya existe")
    if collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email ya existe")
    
    user_dict = user.dict()
    # Hashear la contraseña antes de almacenarla
    user_dict["password"] = get_password_hash(user_dict["password"])
    result = collection.insert_one(user_dict)
    created_user = collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_user)

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 10):
    users = collection.find().skip(skip).limit(limit)
    return [serialize_doc(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return serialize_doc(user)
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UpdateUser):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    
    if 'password' in update_data:
        # Hashear la nueva contraseña
        update_data['password'] = get_password_hash(update_data['password'])
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    updated_user = collection.find_one({"_id": ObjectId(user_id)})
    return serialize_doc(updated_user)

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = collection.delete_one({"_id": ObjectId(user_id)})
    
    if result.deleted_count == 1:
        return {"detail": "Usuario eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
