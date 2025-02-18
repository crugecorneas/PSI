set -o errexit  # exit on error

pip install -r requirements.txt

cd Practica1

python manage.py collectstatic --no-input
python manage.py migrate

# Ejecutar populate solo si no hay datos en la base de datos
python manage.py shell <<EOF
from catalog.models import Book
if not Book.objects.exists():
    print("📚 Populating catalog...")
    import populate_catalog
else:
    print("✅ Database already populated. Skipping populate step.")
EOF
