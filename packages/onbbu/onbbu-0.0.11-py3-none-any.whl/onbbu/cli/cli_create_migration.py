import os
import aerich


def create_migration():
    """Genera una migración para la base de datos"""
    print("📦 Creando migración...")
    # Aquí podrías ejecutar un comando ORM o algún script de migraciones
    os.system("alembic revision --autogenerate -m 'Nueva migración'")