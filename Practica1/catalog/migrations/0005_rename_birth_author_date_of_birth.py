# Generated by Django 4.2.2 on 2025-02-04 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_rename_date_of_birth_author_birth'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='birth',
            new_name='date_of_birth',
        ),
    ]
