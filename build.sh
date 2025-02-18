#!/bin/bash
set -o errexit  # Exit on error

pip install -r requirements.txt

cd Practica1

python manage.py collectstatic --no-input
python manage.py migrate

# Verifica si el usuario 'alumnodb' existe en PostgreSQL
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='alumnodb'" | grep -q 1; then
    echo "El usuario 'alumnodb' no existe. Creándolo..."
    sudo -u postgres psql -c "CREATE ROLE alumnodb WITH SUPERUSER LOGIN PASSWORD 'alumnodb';"
else
    echo "El usuario 'alumnodb' ya existe."
fi

# Verifica si la BD está vacía antes de poblarla
if ! python manage.py shell -c "from catalog.models import Book; exit(0 if Book.objects.exists() else 1)"; then
    echo "La base de datos está vacía. Ejecutando populate_catalog.py..."
    python populate_catalog.py
else
    echo "La base de datos ya está poblada. Saltando populate_catalog.py."
fi
