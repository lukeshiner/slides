from typing import Any

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.core.exceptions import ObjectDoesNotExist
from slides import forms, models


class Index(TemplateView):
    template_name = "slides/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["boxes"] = models.Box.objects.all().order_by("-box_number")
        context["slide_count"] = models.Slide.objects.count()
        return context


class Box(TemplateView):
    template_name = "slides/box.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["box"] = get_object_or_404(
            models.Box, box_number=self.kwargs.get("box_number")
        )
        context["slides"] = context["box"].slides.all()
        context["slide_numbers"] = list(context["slides"].values_list("pk", flat=True))
        return context


class Collections(TemplateView):
    template_name = "slides/collections.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        collections = models.Collection.objects.all()
        context["collections"] = {
            collection: collection.slides.first() for collection in collections
        }
        return context


class Collection(TemplateView):
    template_name = "slides/collection.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["collection"] = get_object_or_404(
            models.Collection, pk=self.kwargs.get("pk")
        )
        context["slides"] = context["collection"].slides.order_by("collection_slides")
        context["slide_numbers"] = list(context["slides"].values_list("pk", flat=True))
        return context


class Years(TemplateView):
    template_name = "slides/years.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        years = (
            models.Box.objects.order_by("year")
            .values_list("year", flat=True)
            .distinct()
        )
        context["years"] = {
            year: models.Slide.objects.by_year(year).first() for year in years
        }
        return context


class Year(TemplateView):
    template_name = "slides/year.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        year = self.kwargs["year"]
        context["years"] = (
            models.Box.objects.order_by("year")
            .values_list("year", flat=True)
            .distinct()
        )
        context["slides"] = models.Slide.objects.by_year(year)
        context["slide_numbers"] = list(context["slides"].values_list("pk", flat=True))
        return context


class ImageViewerImage(View):

    def get(self, *args, **kwargs):
        data = {}
        slide = get_object_or_404(models.Slide, pk=int(self.request.GET["slide_pk"]))
        data["box_number"] = slide.box.box_number
        data["slide_number"] = slide.slide_number
        data["slide"] = slide.box.get_slide(data["slide_number"])
        data["slide_count"] = slide.box.slide_count()
        if data["slide_number"] == 1:
            data["previous_slide_number"] = data["slide_count"]
        else:
            data["previous_slide_number"] = data["slide_number"] - 1
        if data["slide_number"] == data["slide_count"]:
            data["next_slide_number"] = 1
        else:
            data["next_slide_number"] = data["slide_number"] + 1
        return JsonResponse(data)


class AddBox(CreateView):
    template_name = "slides/add_box.html"
    model = models.Box
    form_class = forms.BoxForm

    def get_initial(self):
        initial = super().get_initial()
        initial["box_number"] = (
            models.Box.objects.order_by("-box_number").first().box_number + 1
        )
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()


class AddSlide(CreateView):
    template_name = "slides/add_slide.html"
    model = models.Slide()
    form_class = forms.SlideForm

    def get_initial(self):
        initial = super().get_initial()
        box = get_object_or_404(models.Box, box_number=self.kwargs.get("box_number"))
        box_number = self.kwargs.get("box_number")
        initial["box"] = box.pk
        last_slide = (
            models.Slide.objects.filter(box__box_number=box_number)
            .order_by("-slide_number")
            .first()
        )
        if last_slide is not None:
            initial["slide_number"] = last_slide.slide_number + 1
        else:
            initial["slide_number"] = 1
        return initial

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["box"] = get_object_or_404(
            models.Box, box_number=self.kwargs.get("box_number")
        )
        return context

    def get_success_url(self):
        return reverse("slides:add_slide", args=[self.object.box.box_number])


class UpdateSlide(UpdateView):
    template_name = "slides/update_slide.html"
    model = models.Slide()
    form_class = forms.SlideForm

    def get_object(self):
        return get_object_or_404(
            models.Slide,
            box__box_number=self.kwargs["box_number"],
            slide_number=self.kwargs["slide_number"],
        )

    def get_initial(self):
        initial = super().get_initial()
        if self.object.date:
            initial["date_text"] = self.object.date.strftime("%d %m %y")
        return initial

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["box"] = get_object_or_404(
            models.Box, box_number=self.kwargs.get("box_number")
        )
        context["previous_slide"] = self.get_update_slide_url(
            context["box"], context["form"].instance.slide_number - 1
        )
        context["next_slide"] = self.get_update_slide_url(
            context["box"], context["form"].instance.slide_number + 1
        )
        return context

    def get_update_slide_url(self, box, slide_number):
        try:
            slide = box.slides.get(slide_number=slide_number)
        except ObjectDoesNotExist:
            return None
        else:
            return reverse(
                "slides:update_slide", args=[slide.box.box_number, slide.slide_number]
            )

    def get_success_url(self):
        if url := self.get_update_slide_url(
            self.object.box, self.object.slide_number + 1
        ):
            return url
        else:
            return self.get_update_slide_url(self.object.box, 1)


class AddMissingSlides(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        models.Box.objects.add_slides()
        try:
            return self.request.META["HTTP_REFERER"]
        except Exception:
            return reverse("slides:index")
