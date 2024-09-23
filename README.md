# Reservify

## Descripción
Reservify es una aplicación web para gestionar reservas de manera eficiente, ideal para negocios que necesitan organizar citas o reservas de sus recursos.

## Características
- Registro y autenticación de usuarios.
- Creación, edición y eliminación de reservas.
- Interfaz amigable y fácil de usar.

## Tecnologías Utilizadas
- FastAPI
- MongoDB
- Uvicorn
- Passlib (para hashing de contraseñas)

## Instalación
Crear un entorno virtual
  cd reservify
  python -m venv venv
  source venv/bin/activate  # En Windows usa: venv\Scripts\activate

Instalar las dependencias
  pip install -r requirements.txt

Ejecutar el servidor
  uvicorn app.main:app --reload

## Documentación
Habilitada en http://127.0.0.1:8000/docs (provista por Swagger)

## Licencia
Este proyecto está bajo la Licencia MIT.
