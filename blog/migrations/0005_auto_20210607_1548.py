# Generated by Django 2.2.7 on 2021-06-07 13:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20210607_0313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='latest_post_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
