# Generated by Django 4.2.16 on 2024-11-25 04:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0002_wronglist_list_number"),
    ]

    operations = [
        migrations.RenameField(
            model_name="vocabword", old_name="hirgana", new_name="hiragana",
        ),
    ]
