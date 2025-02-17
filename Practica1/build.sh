set -o errexit  # exit on error

pip install -r Practica1/requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate