from numpy import double
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Resource(BaseModel):
    id: Optional[str] = Field(None, example="Aula Magna")
    name: str = Field(..., example="Aula Magna")
    account_id: str = Field(..., example="60d5ec49f8d4b45f8c1e4e7b")
    info: List[str] = Field(..., example="60d5ec49f8d4b45f8c1e4e7b")
    type: str = Field(..., example="60d5ec49f8d4b45f8c1e4e7b")
    notes: List[str] = Field(..., example="60d5ec49f8d4b45f8c1e4e7b")
    thumbnailUrl: str = Field("", example="60d5ec49f8d4b45f8c1e4e7b")
    price_per_day: float = Field(..., example=40.5)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Aula de Reuniones",
                "account_id": "60d5ec49f8d4b45f8c1e4e7b",
                "info": ["Wifi Banda ancha", "televisión hp 45p"],
                "type": "room",
                "notes": ["Aula equipada con proyector y acceso a internet."],
                "thumbnailUrl": "test"
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ResourceResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str
    account_id: str = Field(..., alias="account_id")
    info: List[str]
    type: str
    notes: List[str]
    thumbnailUrl: str
    rawImagesUrls: List[str]
    price_per_day: float

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "name": "Aula de Reuniones",
                "info": ["Wifi Banda ancha", "televisión hp 45p"],
                "account_id": "60d5ec49f8d4b45f8c1e4e7b",
                "type": "room",
                "notes": ["Aula equipada con proyector y acceso a internet."],
                "thumbnailUrl": "str"
            }
        }

class UpdateResource(BaseModel):
    nombre: Optional[str] = Field(None, example="Aula de Reuniones")
    info: Optional[str] = Field(None, example="Aula equipada con proyector y acceso a internet.")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Aula de Reuniones",
                "info": "Aula equipada con proyector y acceso a internet."
            }
        }
