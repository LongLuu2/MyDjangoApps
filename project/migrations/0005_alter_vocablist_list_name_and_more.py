# Generated by Django 4.2.16 on 2024-12-11 00:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("project", "0004_alter_vocablist_list_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vocablist",
            name="list_name",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name="vocablist", unique_together={("list_name", "user")},
        ),
    ]
