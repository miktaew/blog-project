# Generated by Django 2.2.7 on 2019-12-26 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20191206_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='permissionLevel',
            field=models.TextField(default='user'),
        ),
    ]
