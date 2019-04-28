# Generated by Django 2.1 on 2019-04-26 23:04

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_auto_20190426_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('first_name', models.CharField(help_text='Client first name(s).', max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(help_text="Client's last name.", max_length=255, verbose_name='Last name')),
                ('national_id', models.CharField(help_text='Client National ID number.', max_length=12, validators=[django.core.validators.RegexValidator(message='ID Number should match format like: 58 398766 B 25, without the spaces.', regex='\\d{2}\\d{6,7}[a-zA-Z]{1}\\d{2}')], verbose_name='National ID')),
                ('email_address', models.EmailField(help_text="Client's email address", max_length=255, verbose_name='Email Address')),
                ('phone', models.CharField(help_text="Client's contact phone number.", max_length=10, verbose_name='Phone number')),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], help_text="Client's sex orientation.", max_length=1, verbose_name='Sex')),
                ('address', models.TextField(help_text='Address where services are required.', max_length=255, verbose_name='Address')),
                ('details', models.TextField(help_text='Detailed description of required services or assistance.', max_length=1000, verbose_name='Details')),
                ('lat', models.CharField(editable=False, help_text='Latitude coordinate.', max_length=255, verbose_name='Latitude')),
                ('lng', models.CharField(editable=False, help_text='Longitude coordinate.', max_length=255, verbose_name='Longitude')),
            ],
            options={
                'verbose_name_plural': 'Requests',
            },
        ),
    ]
