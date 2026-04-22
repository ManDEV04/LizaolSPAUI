from config.db import crear_tablas
from services.auth_service import crear_usuario

crear_tablas()

# Usuario de prueba
crear_usuario("Claudia", "Clau1234")

print("Base de datos lista 🚀")