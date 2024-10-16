# Generated by Django 4.2.16 on 2024-10-16 20:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("mini_fb", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_messages",
                        to="mini_fb.profile",
                    ),
                ),
            ],
        ),
    ]
