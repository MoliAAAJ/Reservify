from fastapi import APIRouter, HTTPException, Query, status
from app.models.resource import Resource, ResourceResponse, UpdateResource
from app.database import db, serialize_doc
from bson.objectid import ObjectId
from typing import List, Optional

router = APIRouter(
    prefix="/resources",
    tags=["Resources"]
)

collection = db["resources"]

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(resource: Resource):
    # Verificar si el nombre del recurso ya existe
    if collection.find_one({"nombre": resource.name}):
        raise HTTPException(status_code=400, detail="El nombre del recurso ya existe")
    
    resource_dict = resource.dict()
    result = collection.insert_one(resource_dict)
    created_resource = collection.find_one({"_id": result.inserted_id})
    return serialize_doc(created_resource)

@router.get("/", response_model=List[ResourceResponse])
def get_resources(skip: int = 0, 
                  limit: int = 10, 
                  company_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b")):
    query = {}
    if company_id:
        if not ObjectId.is_valid(company_id):
            raise HTTPException(status_code=400, detail="company_id inválido")
        query['company_id'] = ObjectId(company_id)
        
    resources = collection.find(query).skip(skip).limit(limit)
    resource_list = [serialize_doc(resource) for resource in resources]
    return resource_list

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: str):
    if not ObjectId.is_valid(resource_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    resource = collection.find_one({"_id": ObjectId(resource_id)})
    if resource:
        return serialize_doc(resource)
    else:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: str, resource: UpdateResource):
    if not ObjectId.is_valid(resource_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = {k: v for k, v in resource.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    # Verificar si el nombre del recurso a actualizar ya existe en otro documento
    if "nombre" in update_data:
        existing_resource = collection.find_one({"nombre": update_data["nombre"], "_id": {"$ne": ObjectId(resource_id)}})
        if existing_resource:
            raise HTTPException(status_code=400, detail="El nombre del recurso ya existe")
    
    result = collection.update_one({"_id": ObjectId(resource_id)}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    
    updated_resource = collection.find_one({"_id": ObjectId(resource_id)})
    return serialize_doc(updated_resource)

@router.delete("/{resource_id}", response_model=dict)
def delete_resource(resource_id: str):
    if not ObjectId.is_valid(resource_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = collection.delete_one({"_id": ObjectId(resource_id)})
    
    if result.deleted_count == 1:
        return {"detail": "Recurso eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
