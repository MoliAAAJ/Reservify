
from bson import ObjectId
from pydantic import BaseModel, Field


class Company(BaseModel):
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "LogiTech"
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
        
class CompanyResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "name": "LogiTech",
            }
        }
