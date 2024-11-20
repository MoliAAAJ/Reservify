import json
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from image_utils import create_thumbnail_from_upload
from services.blob.blob_service import delete_blob_from_url, upload_image
from models.resource import Resource, ResourceResponse, UpdateResource
from database import db, serialize_doc
from bson.objectid import ObjectId
from typing import Any, List, Optional

router = APIRouter(
    prefix="/resources",
    tags=["Resources"]
)

collection = db["resources"]

@router.post("/", response_model= ResourceResponse)
async def create_resource(
    resource_data: str = Form(...),
    images: List[UploadFile] = File(...)
):
    resource = json.loads(resource_data)
    result = collection.insert_one(resource)
    resource_id = str(result.inserted_id)
    
    # Upload thumbnail (first image)
    if images:
        thumbnail_url = await upload_image(create_thumbnail_from_upload(images[0]), resource_id, is_thumbnail=True)
        resource["thumbnailUrl"] = thumbnail_url
        
        # Upload raw images
        raw_urls = []
        for image in images:
            url = await upload_image(image, resource_id)
            raw_urls.append(url)
        resource["rawImagesUrls"] = raw_urls
    
    resource['account_id'] = ObjectId(resource['account_id'])
    if not collection.find_one({ "account_id": resource['account_id']}):
        raise HTTPException(status_code=400, detail="account_id inválido")
    
    collection.update_one({"_id": ObjectId(resource_id)}, {"$set": resource})
    
    resource["id"] = resource_id
    
    return serialize_doc(resource)

@router.put("/{resource_id}", response_model= ResourceResponse)
async def update_resource(
    resource_id: str,
    resource_data: str = Form(...),
    images: List[UploadFile] = File(None)
):
    resource: Resource = json.loads(resource_data)
    
    # Handle new images if provided
    if images:
        new_raw_urls = []
        for image in images:
            try:
                url = await upload_image(image, resource_id)
            except Exception:
                raise HTTPException(status_code=400, detail="Error uploading image")
            new_raw_urls.append(url)
        resource["rawImagesUrls"].extend(new_raw_urls)
    
    resource["account_id"] = ObjectId(resource["account_id"])
    collection.update_one(
        {"_id": ObjectId(resource_id)},
        {"$set": resource}
    )
    
    return serialize_doc(resource)
    
@router.get("/", response_model=List[ResourceResponse])
def get_resources(skip: int = 0, 
                  limit: int = 10, 
                  account_id: Optional[str] = Query(None, example="60d5ec49f8d4b45f8c1e4e7b")):
    query = {}
    if account_id:
        if not ObjectId.is_valid(account_id):
            raise HTTPException(status_code=400, detail="account_id inválido")
        query['account_id'] = ObjectId(account_id)
        
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
    
    

@router.delete("/{resource_id}/images")
async def remove_image(resource_id: str, image_url: str):
    # Remove image URL from resource
    resource = await db.resources.find_one_and_update(
        {"_id": resource_id},
        {"$pull": {"rawImagesUrls": image_url}},
        return_document=True
    )
    
    # Delete the image from Azure Blob Storage
    await delete_blob_from_url(image_url)
    
    return resource


@router.delete("/{resource_id}", response_model=dict)
def delete_resource(resource_id: str):
    if not ObjectId.is_valid(resource_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = collection.delete_one({"_id": ObjectId(resource_id)})
    
    if result.deleted_count == 1:
        return {"detail": "Recurso eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
