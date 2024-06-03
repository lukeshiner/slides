"""URLs for the slides app."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from slides import views

app_name = "slides"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("box/<int:box_number>", views.Box.as_view(), name="box"),
    path("add_box", views.AddBox.as_view(), name="add_box"),
    path("add_slide/<int:box_number>", views.AddSlide.as_view(), name="add_slide"),
    path(
        "update_slide/<int:box_number>/<int:slide_number>",
        views.UpdateSlide.as_view(),
        name="update_slide",
    ),
    path(
        "image_viewer_image",
        views.ImageViewerImage.as_view(),
        name="image_viewer_image",
    ),
    path("years", views.Years.as_view(), name="years"),
    path("year/<int:year>", views.Year.as_view(), name="year"),
    path("collections", views.Collections.as_view(), name="collections"),
    path("collection/<int:pk>", views.Collection.as_view(), name="collection"),
    path(
        "add_missing_sllides",
        views.AddMissingSlides.as_view(),
        name="add_missing_slides",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.SLIDE_MEDIA_URL, document_root=settings.SLIDE_MEDIA_ROOT)
urlpatterns += static(settings.THUMB_MEDIA_URL, document_root=settings.THUMB_MEDIA_ROOT)
