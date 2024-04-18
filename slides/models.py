import datetime as dt

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.shortcuts import reverse


class Box(models.Model):
    """Model for boxes or other containers of slides."""

    box_number = models.PositiveIntegerField()
    label = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    developed = models.DateField(blank=True, null=True)

    class BoxManager(models.Manager):
        @transaction.atomic()
        def add_slides(self):
            for box in self.all():
                box.add_slides()

    objects = BoxManager()

    class Meta:
        verbose_name = "Box"
        verbose_name_plural = "Boxes"
        ordering = ("box_number",)

    def __str__(self):
        return self.name()

    def get_absolute_url(self):
        return reverse("slides:box", args=[self.box_number])

    def name(self):
        return f"{self.box_number:04d}"

    def developed_readable(self):
        if self.developed is not None:
            return self.developed.strftime("%b %y")
        return ""

    def slide_directory(self):
        return settings.SLIDE_MEDIA_ROOT / self.name()

    def thumb_directory(self):
        return settings.THUMB_MEDIA_ROOT / self.name()

    def slide_directory_count(self):
        try:
            return len(list(self.slide_directory().iterdir()))
        except FileNotFoundError:
            return 0

    def db_slide_count(self):
        slide = self.slides.all().order_by("-slide_number").first()
        if slide is not None:
            return slide.slide_number
        return 0

    def slide_count(self):
        return max(self.slide_directory_count(), self.db_slide_count())

    def slide_name(self, slide_number):
        return f"{self.name()}_{slide_number:03d}"

    def slide_url(self, slide_number):
        return f"{settings.SLIDE_MEDIA_URL}{self.name()}/{self.slide_name(slide_number)}.jpg"

    def thumb_url(self, slide_number):
        return f"{settings.THUMB_MEDIA_URL}{self.name()}/{self.slide_name(slide_number)}_thumb.jpg"

    def get_slide(self, slide_number):
        data = {
            "name": self.slide_name(slide_number),
            "number": slide_number,
            "slide_url": self.slide_url(slide_number),
            "thumb_url": self.thumb_url(slide_number),
            "date": "",
            "notes": "",
        }
        try:
            slide_obj = Slide.objects.get(box=self, slide_number=slide_number)
        except Slide.DoesNotExist:
            pass
        else:
            if slide_obj.date:
                data["date"] = slide_obj.date.strftime("%d %b %Y")
            if slide_obj.notes:
                data["notes"] = slide_obj.notes
        return data

    def first_slide(self):
        return self.get_slide(1)

    def get_slides(self):
        images = []
        for i in range(1, self.slide_count() + 1):
            images.append(self.get_slide(i))
        return images

    def next_box(self):
        return (
            Box.objects.filter(box_number__gt=self.box_number)
            .order_by("box_number")
            .first()
        )

    def previous_box(self):
        return (
            Box.objects.filter(box_number__lt=self.box_number)
            .order_by("box_number")
            .last()
        )

    @transaction.atomic()
    def add_slides(self):
        existing_slides = self.slides.values_list("slide_number", flat=True)
        for slide_number in range(1, self.slide_directory_count()):
            if slide_number in existing_slides:
                continue
            Slide(box=self, slide_number=slide_number).save()


class Slide(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="slides")
    slide_number = models.PositiveIntegerField()
    date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    marked = models.BooleanField(default=False)

    class SlideManager(models.Manager):
        def by_year(self, year):
            return self.filter(
                Q(date__year=year) | Q(box__year=year) | Q(box__developed__year=year)
            ).order_by(
                "box__developed", "box__year", "box__box_number", "date", "slide_number"
            )

    objects = SlideManager()

    class Meta:
        verbose_name = "Slide"
        verbose_name_plural = "Slides"
        unique_together = [["box", "slide_number"]]
        ordering = ("slide_number",)

    def __str__(self):
        return self.name()

    def name(self):
        return self.box.slide_name(self.slide_number)

    def thumb_url(self):
        return f"{settings.THUMB_MEDIA_URL}{self.box.name()}/{self.name()}_thumb.jpg"


class Collection(models.Model):
    name = models.CharField(max_length=255)
    slides = models.ManyToManyField(Slide, through="CollectionSlide")
    collection_order = models.PositiveIntegerField(default=0)

    class CollectionManager(models.Manager):
        @transaction.atomic()
        def from_boxes(self, name, box_numbers):
            max_slide_order = (
                CollectionSlide.objects.order_by("slide_order").last().slide_order
            )
            collection = self.create(name=name)
            boxes = [Box.objects.get(box_number=_) for _ in box_numbers]
            slide_number = 1
            for box in boxes:
                for slide in box.slides.order_by("slide_number"):
                    CollectionSlide.objects.create(
                        collection=collection,
                        slide=slide,
                        slide_order=max_slide_order + slide_number,
                    )
                    slide_number += 1
            return collection

    objects = CollectionManager()

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
        ordering = ("collection_order",)

    def __str__(self):
        return self.name


class CollectionSlide(models.Model):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="collection_slides"
    )
    slide = models.ForeignKey(
        Slide, on_delete=models.CASCADE, related_name="collection_slides"
    )
    slide_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Collection Slide"
        verbose_name_plural = "Collection Slides"
        ordering = ("slide_order",)

    def __str__(self):
        return f"{self.slide_order}: {self.slide.notes} - {self.slide.date}"
