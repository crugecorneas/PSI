#!/bin/bash
set -o errexit  # exit on error

pip install -r requirements.txt

cd Practica1

python manage.py collectstatic --no-input
python manage.py migrate

echo "Verificando si el superusuario alumnodb ya existe..."
EXISTING_USER=$(echo "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username='alumnodb').exists())" | python manage.py shell)

if [ "$EXISTING_USER" = "True" ]; then
    echo "El superusuario alumnodb ya existe."
else
    echo "Creando superusuario de Django..."
    python manage.py createsuperuser --no-input
fi

# Verifica si la BD está vacía antes de poblarla
if ! python manage.py shell -c "from catalog.models import Book; exit(0 if Book.objects.exists() else 1)"; then
    echo "La base de datos está vacía. Ejecutando populate_catalog.py..."
    python populate_catalog.py
else
    echo "La base de datos ya está poblada."
fi
