# Generated by Django 4.2.16 on 2024-11-26 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0003_rename_hirgana_vocabword_hiragana"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vocablist",
            name="list_name",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
