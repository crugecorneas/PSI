#!/bin/bash
set -o errexit  # exit on error

pip install -r requirements.txt

cd Practica1

python manage.py collectstatic --no-input
python manage.py migrate

echo "Creando superusuario de Django..."
python manage.py createsuperuser --no-input || echo "El superusuario ya existe."


# Verifica si la BD está vacía antes de poblarla
if ! python manage.py shell -c "from catalog.models import Book; exit(0 if Book.objects.exists() else 1)"; then
    echo "La base de datos está vacía. Ejecutando populate_catalog.py..."
    python populate_catalog.py
else
    echo "La base de datos ya está poblada. Saltando populate_catalog.py."
fi
