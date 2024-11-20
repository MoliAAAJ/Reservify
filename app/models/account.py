from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class Account(BaseModel):
    name: str = Field(..., example="Juan Pérez")
    email: EmailStr = Field(..., example="juan.perez@example.com")
    username: str = Field(..., example="juanperez")
    password: str = Field(..., example="ContraseñaSegura123")
    account_type: str =  Field(..., example="company")
    thumbnailUrl: str = Field(..., example="https://thumbnail.src.com")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "username": "juanperez",
                "password": "ContraseñaSegura123",
                "account_type": "COMPANY",
                "thumbnail": "https://thumbnail.src.com"
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AccountResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    account_type: str
    thumbnailUrl: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7a",
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "username": "juanperez",
                "is_active": True,
                "account_type": "COMPANY",
                "thumbnail": "https://thumbnail.src.com"
            }
        }

class UpdateAccount(BaseModel):
    name: Optional[str] = Field(None, example="Juan Pérez")
    email: Optional[EmailStr] = Field(None, example="juan.perez@example.com")
    username: Optional[str] = Field(None, example="juanperez")
    password: Optional[str] = Field(None, example="NuevaContraseña123")
    is_active: Optional[bool] = Field(None, example=True)
    account_type: Optional[str] = Field(None, example="COMPANY")
    thumbnailUrl: Optional[str] = Field(None, example="https://thumbnail.src.com")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@example.com",
                "username": "juanperez",
                "password": "NuevaContraseña123",
                "is_active": True,
                "account_type": "COMPANY",
                "thumbnail": "https://thumbnail.src.com"
            }
        }


class ClientAccountResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field('user', example="Juan Pérez")
    email: EmailStr = Field('email', example="juan.perez@example.com")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7a",
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",

            }
        }
        

class CompanyAccountResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field('user', example="Juan Pérez")
    email: EmailStr = Field('email', example="juan.perez@example.com")
    thumbnailUrl: str = Field(..., example="https://thumbnail.src.com")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7a",
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",

            }
        }