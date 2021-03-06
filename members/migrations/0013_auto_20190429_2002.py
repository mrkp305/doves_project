# Generated by Django 2.1 on 2019-04-29 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_auto_20190428_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='place_of_death',
            field=models.CharField(help_text='Place where policy dependant died.', max_length=255, verbose_name='Place of death'),
        ),
        migrations.AlterField(
            model_name='request',
            name='lat',
            field=models.CharField(help_text='Latitude coordinate.', max_length=255, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='request',
            name='lng',
            field=models.CharField(help_text='Longitude coordinate.', max_length=255, verbose_name='Longitude'),
        ),
    ]
