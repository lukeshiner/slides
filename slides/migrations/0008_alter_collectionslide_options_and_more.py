# Generated by Django 5.0.4 on 2024-04-15 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("slides", "0007_collection_alter_box_options_collectionslide_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="collectionslide",
            options={
                "ordering": ("slide_order",),
                "verbose_name": "Collection Slide",
                "verbose_name_plural": "Collection Slides",
            },
        ),
        migrations.RenameField(
            model_name="collectionslide",
            old_name="ordering",
            new_name="slide_order",
        ),
    ]
