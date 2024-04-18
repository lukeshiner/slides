from adminsortable2.admin import (
    SortableAdminBase,
    SortableAdminMixin,
    SortableInlineAdminMixin,
)
from django.contrib import admin

from slides import models


@admin.register(models.Box)
class BoxAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ("__str__", "box_number", "label", "notes", "year", "developed")
    list_filter = ("year",)


@admin.register(models.Slide)
class SlideAdmin(admin.ModelAdmin):
    exclude = ()
    list_display = ("__str__", "box", "slide_number", "notes", "date")
    list_editable = ("box", "slide_number", "notes", "date")
    list_filter = ("box",)


class SlideTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    model = models.CollectionSlide
    raw_id_fields = ("slide",)
    readonly_fields = ("__str__",)


@admin.register(models.Collection)
class CollectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = (SlideTabularInline,)
