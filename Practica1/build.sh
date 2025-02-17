#!/bin/bash

# Salir si ocurre un error
set -e

# Cargar variables de entorno desde el archivo .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Aplicar migraciones de la base de datos
echo "Aplicando migraciones..."
python manage.py migrate

# Crear superusuario si no existe
echo "Creando superusuario..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
if not User.objects.filter(username='alumnodb').exists(): \
    User.objects.create_superuser('alumnodb', 'admin@example.com', 'alumnodb')" | python manage.py shell

# Poblar la base de datos si es necesario
echo "Poblando la base de datos..."
python manage.py loaddata initial_data.json

echo "Configuración completa."
