from bson import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URI de MongoDB y el nombre de la base de datos desde las variables de entorno
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Validar que las variables de entorno estén definidas
if not MONGODB_URI or not DATABASE_NAME:
    raise ValueError("Las variables de entorno MONGODB_URI y DATABASE_NAME deben estar definidas en el archivo .env")

# Establecer la conexión con MongoDB
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Función para serializar documentos de MongoDB, convirtiendo ObjectId a string
def serialize_doc(doc):
    res = {}
    if doc:
        for key, value in doc.items():
            if key == '_id':
                    key = 'id'
            if isinstance(value, ObjectId):
                value = str(value)
            res[key] = value
    return res
