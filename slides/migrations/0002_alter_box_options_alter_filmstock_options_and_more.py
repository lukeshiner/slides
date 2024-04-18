# Generated by Django 5.0.4 on 2024-04-07 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("slides", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="box",
            options={
                "ordering": ("year", "developed"),
                "verbose_name": "Box",
                "verbose_name_plural": "Boxes",
            },
        ),
        migrations.AlterModelOptions(
            name="filmstock",
            options={"verbose_name": "Filmstock", "verbose_name_plural": "Filmstocks"},
        ),
        migrations.AlterField(
            model_name="box",
            name="year",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]