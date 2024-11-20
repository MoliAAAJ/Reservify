from ast import parse
from fastapi import APIRouter, HTTPException, status, Query
from assignement_utils import get_overlapping_query
from models.assignment import Assignment, AssignmentResponse, UpdateAssignment
from database import db, serialize_doc
from bson import ObjectId
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)

collection = db["assignments"]
accounts_collection = db["accounts"]
resources_collection = db["resources"]

def is_overlapping(resource_id: str, start_time: datetime, end_time: datetime, exclude_id: Optional[str] = None) -> bool:
    query = {
        "resource_id": ObjectId(resource_id),
        "$or": get_overlapping_query(start_time, end_time)
    }
    if exclude_id:
        query["_id"] = {"$ne": ObjectId(exclude_id)}
    overlapping = collection.find_one(query)
    return overlapping is not None

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment: Assignment):
    # Validar account_id
    if not ObjectId.is_valid(assignment.account_id):
        raise HTTPException(status_code=400, detail="account_id inválido")
    account = accounts_collection.find_one({"_id": ObjectId(assignment.account_id)})
    if not account:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar resource_id
    if not ObjectId.is_valid(assignment.resource_id):
        raise HTTPException(status_code=400, detail="resource_id inválido")
    resource = resources_collection.find_one({"_id": ObjectId(assignment.resource_id)})
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    

    
    # Validar que no haya reservas superpuestas
    if is_overlapping(assignment.resource_id, assignment.start_time, assignment.end_time):
        raise HTTPException(status_code=400, detail="La reserva se solapa con una existente para este recurso")
    
    assignment_dict = assignment.dict()
    assignment_dict = assignment.dict()
    assignment_dict['status'] = 'pending'
    assignment_dict['account_id'] = ObjectId(assignment_dict['account_id'])
    assignment_dict['resource_id'] = ObjectId(assignment_dict['resource_id'])
    result = collection.insert_one(assignment_dict)
    created_assignment = collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_assignment)

@router.get("/")
async def get_bookings(
    start_date: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7a"),
    end_date: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7a"), 
    skip: int = 0,
    limit: int = 10,
    account_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7a"),
    resource_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b"),

    ) -> List[AssignmentResponse]:
    """
    Get all bookings for a specific resource and date
    """
    query = {}
    
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        query["$or"] = get_overlapping_query(start, end)
    
    if account_id:
        if not ObjectId.is_valid(account_id):
            raise HTTPException(status_code=400, detail="account_id inválido")
        query["account_id"] = ObjectId(account_id)
    if resource_id:
        if not ObjectId.is_valid(resource_id):
            raise HTTPException(status_code=400, detail="resource_id inválido")
        query["resource_id"] = ObjectId(resource_id)
    
    

    assignments = collection.find(query).skip(skip).limit(limit)
    
    return [serialize_doc(booking) for booking in assignments]


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: str):
    if not ObjectId.is_valid(assignment_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    assignment = collection.find_one({"_id": ObjectId(assignment_id)})
    if assignment:
        return serialize_doc(assignment)
    else:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

@router.put("/", response_model=AssignmentResponse)
def update_assignment(assignment: UpdateAssignment):
    if not ObjectId.is_valid(assignment.id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    existing_assignment = collection.find_one({"_id": ObjectId(assignment.id)})
    if not existing_assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    update_data = {k: v for k, v in assignment.dict().items() if v is not None}
    
    assignment_id = update_data.pop('id')
    
    if 'account_id' in update_data:
        if not ObjectId.is_valid(update_data['account_id']):
            raise HTTPException(status_code=400, detail="account_id inválido")
        account = accounts_collection.find_one({"_id": ObjectId(update_data['account_id'])})
        if not account:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if 'resource_id' in update_data:
        if not ObjectId.is_valid(update_data['resource_id']):
            raise HTTPException(status_code=400, detail="resource_id inválido")
        resource = resources_collection.find_one({"_id": ObjectId(update_data['resource_id'])})
        if not resource:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
    
    # Si se actualizan start_time o end_time o resource_id, verificar solapamientos
    new_resource_id = update_data.get('resource_id', existing_assignment['resource_id'])
    new_start_time = update_data.get('start_time', existing_assignment['start_time'])
    new_end_time = update_data.get('end_time', existing_assignment['end_time'])
    
    if is_overlapping(new_resource_id, new_start_time, new_end_time, exclude_id=assignment_id):
        raise HTTPException(status_code=400, detail="La reserva se solapa con una existente para este recurso")
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = collection.update_one({"_id": ObjectId(assignment_id)}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    updated_assignment = collection.find_one({"_id": ObjectId(assignment_id)})
    return serialize_doc(updated_assignment)

@router.delete("/{assignment_id}", response_model=dict)
def delete_assignment(assignment_id: str):
    if not ObjectId.is_valid(assignment_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = collection.delete_one({"_id": ObjectId(assignment_id)})
    
    if result.deleted_count == 1:
        return {"detail": "Asignación eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    

@router.get("/check-availability/")
async def check_availability(
    resource_id: str,
    start_time: str,
    end_time: str
) -> bool:
    """
    Check if a time slot is available for booking
    """
    try:
        start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        end = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as ve:
        
            raise HTTPException(status_code=400, detail=f"Invalid date format: {ve}")

    if start >= end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    # Check for overlapping bookings
    overlapping = collection.find_one({
        "resource_id": ObjectId(resource_id),
        "status": {"$in": ["pending", "active"]},
        "$or": get_overlapping_query(start, end)
    })

    return overlapping is None
