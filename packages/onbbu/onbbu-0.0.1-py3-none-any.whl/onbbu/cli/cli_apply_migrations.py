import os


def apply_migrations():
    """Aplica migraciones a la base de datos"""
    print("📦 Aplicando migraciones...")
    os.system("alembic upgrade head")
