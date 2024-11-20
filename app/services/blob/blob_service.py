# Azure Blob Storage connection
import hashlib
import os
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from fastapi import UploadFile


AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=reservify;AccountKey=Qt7CYNn0JtC7GFH+aOvXD+yv3sjCMVLLw6rmak0Ir7nBFARP59SI5+clILSkrAtfvoerLZ1vUWLv+ASto2KxDA==;EndpointSuffix=core.windows.net;"
CONTAINER_NAME = "images"
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

async def get_image_hash(file_contents: bytes) -> str:
    return hashlib.md5(file_contents).hexdigest()

async def upload_image(file: UploadFile, resource_id: str, is_thumbnail: bool = False) -> str:
    contents = await file.read()
    file_hash = await get_image_hash(contents)
    
    # Include resource_id in blob name to ensure uniqueness per resource
    blob_name = f"{resource_id}/{'thumbnails' if is_thumbnail else 'raw'}/{file_hash}{os.path.splitext(file.filename)[1]}"
    
    try:
        blob_client = container_client.get_blob_client(blob_name)
        await file.seek(0)
        blob_client.upload_blob(contents, content_settings=ContentSettings(content_type=file.content_type))
    except ResourceExistsError:
        pass
    
    return f"{container_client.url}/{blob_name}"

async def delete_blob_from_url(url: str):
    # Extract blob name from URL
    blob_name = url.split(f"{container_client.url}/")[1]
    blob_client = container_client.get_blob_client(blob_name)
    try:
        blob_client.delete_blob()
    except Exception as e:
        print(f"Error deleting blob: {e}")