# Generated by Django 2.2.7 on 2020-01-02 03:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20191230_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
            preserve_default=False,
        ),
    ]
