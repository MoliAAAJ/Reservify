from fastapi import APIRouter, HTTPException, status, Query
from models.assignment import Assignment, AssignmentResponse, UpdateAssignment
from database import db, serialize_doc
from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)

collection = db["assignments"]
users_collection = db["users"]
resources_collection = db["resources"]

def is_overlapping(resource_id: str, start_time: datetime, end_time: datetime, exclude_id: Optional[str] = None) -> bool:
    query = {
        "resource_id": resource_id,
        "$or": [
            {
                "start_time": {"$lt": end_time},
                "end_time": {"$gt": start_time}
            }
        ]
    }
    if exclude_id:
        query["_id"] = {"$ne": ObjectId(exclude_id)}
    overlapping = collection.find_one(query)
    return overlapping is not None

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment: Assignment):
    # Validar user_id
    if not ObjectId.is_valid(assignment.user_id):
        raise HTTPException(status_code=400, detail="user_id inválido")
    user = users_collection.find_one({"_id": ObjectId(assignment.user_id)})
    if not user:
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
    assignment_dict['status'] = 'pending'
    result = collection.insert_one(assignment_dict)
    created_assignment = collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_assignment)

@router.get("/", response_model=List[AssignmentResponse])
def get_assignments(
    skip: int = 0,
    limit: int = 10,
    user_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7a"),
    resource_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b"),
    company_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b"),
    start_after: Optional[datetime] = Query(None, example="2024-05-01T00:00:00Z"),
    start_before: Optional[datetime] = Query(None, example="2024-05-31T23:59:59Z")
):
    query = {}
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="user_id inválido")
        query["user_id"] = ObjectId(user_id)
    if resource_id:
        if not ObjectId.is_valid(resource_id):
            raise HTTPException(status_code=400, detail="resource_id inválido")
        query["resource_id"] = resource_id
    if start_after:
        query["start_time"] = {"$gte": start_after}
    if start_before:
        if "start_time" in query:
            query["start_time"]["$lte"] = start_before
        else:
            query["start_time"] = {"$lte": start_before}
    
    assignments = collection.find(query).skip(skip).limit(limit)
    return [serialize_doc(assignment) for assignment in assignments]

@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: str):
    if not ObjectId.is_valid(assignment_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    assignment = collection.find_one({"_id": ObjectId(assignment_id)})
    if assignment:
        return serialize_doc(assignment)
    else:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(assignment_id: str, assignment: UpdateAssignment):
    if not ObjectId.is_valid(assignment_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    existing_assignment = collection.find_one({"_id": ObjectId(assignment_id)})
    if not existing_assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    update_data = {k: v for k, v in assignment.dict().items() if v is not None}
    
    if 'user_id' in update_data:
        if not ObjectId.is_valid(update_data['user_id']):
            raise HTTPException(status_code=400, detail="user_id inválido")
        user = users_collection.find_one({"_id": ObjectId(update_data['user_id'])})
        if not user:
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
