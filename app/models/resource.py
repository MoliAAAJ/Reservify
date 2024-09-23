from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class Resource(BaseModel):
    nombre: str = Field(..., example="Aula Magna")
    info: Optional[str] = Field(None, example="Aula equipada con proyector y acceso a internet.")

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Aula de Reuniones",
                "info": "Aula equipada con proyector y acceso a internet."
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ResourceResponse(BaseModel):
    id: str = Field(..., alias="_id")
    nombre: str
    info: Optional[str]

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "nombre": "Aula de Reuniones",
                "info": "Aula equipada con proyector y acceso a internet."
            }
        }

class UpdateResource(BaseModel):
    nombre: Optional[str] = Field(None, example="Aula de Reuniones")
    info: Optional[str] = Field(None, example="Aula equipada con proyector y acceso a internet.")

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Aula de Reuniones",
                "info": "Aula equipada con proyector y acceso a internet."
            }
        }
