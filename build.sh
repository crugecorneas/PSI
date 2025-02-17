set -o errexit  # exit on error

pip install -r requirements.txt

cd Practica1
python manage.py collectstatic --no-input
python manage.py migrate