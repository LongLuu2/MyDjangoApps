# Generated by Django 4.2.16 on 2024-11-22 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="wronglist",
            name="list_number",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]