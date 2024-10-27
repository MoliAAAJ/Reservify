from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    nombre: str = Field(..., example="Juan Pérez")
    email: EmailStr = Field(..., example="juan.perez@example.com")
    username: str = Field(..., example="juanperez")
    password: str = Field(..., example="ContraseñaSegura123")

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "username": "juanperez",
                "password": "ContraseñaSegura123"
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserResponse(BaseModel):
    id: str = Field(..., alias="id")
    nombre: str
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    permissions: str

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7a",
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "username": "juanperez",
                "is_active": True,
                "permissions": "ADMIN"
            }
        }

class UpdateUser(BaseModel):
    nombre: Optional[str] = Field(None, example="Juan Pérez")
    email: Optional[EmailStr] = Field(None, example="juan.perez@example.com")
    username: Optional[str] = Field(None, example="juanperez")
    password: Optional[str] = Field(None, example="NuevaContraseña123")
    is_active: Optional[bool] = Field(None, example=True)

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "username": "juanperez",
                "password": "NuevaContraseña123",
                "is_active": True
            }
        }
