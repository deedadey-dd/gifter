# Generated by Django 5.0.7 on 2024-08-12 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='password',
            field=models.CharField(default='1234gifted1234', max_length=255),
        ),
    ]
