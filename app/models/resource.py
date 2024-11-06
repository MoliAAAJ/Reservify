from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Resource(BaseModel):
    name: str = Field(..., example="Aula Magna")
    info: List[str]
    type: str
    company_id: str
    notes: List[str]


    class Config:
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "name": "Aula de Reuniones",
                "info": ["Wifi Banda ancha", "televisión hp 45p"],
                "companyId": "60d5ec49f8d4b45f8c1e4e7b",
                "type": "room",
                "notes": ["Aula equipada con proyector y acceso a internet."]
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ResourceResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str
    info: List[str]
    type: str
    company_id: str = Field(..., alias="company_id")
    notes: List[str]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "name": "Aula de Reuniones",
                "info": ["Wifi Banda ancha", "televisión hp 45p"],
                "company_id": "60d5ec49f8d4b45f8c1e4e7b",
                "type": "room",
                "notes": ["Aula equipada con proyector y acceso a internet."],
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
