from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Assignment(BaseModel):
    user_id: str = Field(..., example="60d5ec49f8d4b45f8c1e4e7a")
    resource_id: str = Field(..., example="60d5ec49f8d4b45f8c1e4e7b")
    start_time: datetime = Field(..., example="2024-05-01T10:00:00Z")
    end_time: datetime = Field(..., example="2024-05-01T12:00:00Z")
    notes: Optional[str] = Field(None, example="Reserva para reunión de equipo.")
    status: Optional[str] = Field("unknown", example="Reserva para reunión de equipo.")

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('end_time debe ser posterior a start_time')
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": "60d5ec49f8d4b45f8c1e4e7a",
                "resource_id": "60d5ec49f8d4b45f8c1e4e7b",
                "start_time": "2024-05-01T10:00:00Z",
                "end_time": "2024-05-01T12:00:00Z",
                "notes": "Reserva para reunión de equipo.",
                "status": "pending"
            }
        }
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AssignmentResponse(BaseModel):
    id: str = Field(..., alias="id")
    user_id: str
    resource_id: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str]
    status: Optional[str]

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "60d5ec49f8d4b45f8c1e4e7c",
                "user_id": "60d5ec49f8d4b45f8c1e4e7a",
                "resource_id": "60d5ec49f8d4b45f8c1e4e7b",
                "start_time": "2024-05-01T10:00:00Z",
                "end_time": "2024-05-01T12:00:00Z",
                "notes": "Reserva para reunión de equipo.",
                "status": "pending"
            }
        }

class UpdateAssignment(BaseModel):
    user_id: Optional[str] = Field(None, example="60d5ec49f8d4b45f8c1e4e7a")
    resource_id: Optional[str] = Field(None, example="60d5ec49f8d4b45f8c1e4e7b")
    start_time: Optional[datetime] = Field(None, example="2024-05-01T10:00:00Z")
    end_time: Optional[datetime] = Field(None, example="2024-05-01T12:00:00Z")
    notes: Optional[str] = Field(None, example="Reserva para reunión de equipo.")

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        start_time = values.get('start_time')
        if start_time and v and v <= start_time:
            raise ValueError('end_time debe ser posterior a start_time')
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": "60d5ec49f8d4b45f8c1e4e7a",
                "resource_id": "60d5ec49f8d4b45f8c1e4e7b",
                "start_time": "2024-05-01T10:00:00Z",
                "end_time": "2024-05-01T12:00:00Z",
                "notes": "Reserva para reunión de equipo."
            }
        }
