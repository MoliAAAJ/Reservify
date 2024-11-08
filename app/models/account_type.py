from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class Account_type(BaseModel):
    user_id: str
    account_type: str = Field(..., example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "account_type": "admin"
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Account_typeResponse(BaseModel):
    id: str = Field(..., alias="id")
    user_id: str = Field(..., alias="user_id")
    account_type: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7b",
                "user_id": "60d5ec49f8d4b45f8c1e4e7b",
                "account_type": "admin"
            }
        }

class UpdateAccount_type(BaseModel):
    account_type: Optional[str] = Field(None, example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "account_type": "admin"
            }
        }
