# Generated by Django 3.1.3 on 2021-12-16 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpay',
            name='pay',
            field=models.BooleanField(default=False),
        ),
    ]
