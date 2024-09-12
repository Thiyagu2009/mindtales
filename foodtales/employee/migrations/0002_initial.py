# Generated by Django 5.1.1 on 2024-09-11 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0001_initial'),
        ('restaurant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='restaurant.menu'),
        ),
    ]
