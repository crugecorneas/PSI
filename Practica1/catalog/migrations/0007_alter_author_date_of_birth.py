# Generated by Django 4.2.2 on 2025-02-04 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_author_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True,
                                   verbose_name='birth'),
        ),
    ]
