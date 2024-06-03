import datetime as dt

from django import forms

from slides import models


class BoxForm(forms.ModelForm):

    developed_text = forms.CharField(required=False)

    class Meta:
        model = models.Box
        exclude = ()
        widgets = {"developed": forms.HiddenInput()}

    def clean(self):
        super().clean()
        text = self.cleaned_data.get("developed_text")
        if text:
            self.cleaned_data["developed"] = dt.datetime.strptime(text, "%b %y").date()
        else:
            self.cleaned_data["developed"] = None
        return self.cleaned_data


class SlideForm(forms.ModelForm):
    date_text = forms.CharField(required=False)

    class Meta:
        model = models.Slide
        exclude = ("marked",)
        widgets = {"box": forms.HiddenInput(), "date": forms.HiddenInput()}

    def clean(self):
        super().clean()
        text = self.cleaned_data.get("date_text")
        if text:
            date = dt.datetime.strptime(text, "%d %m %y").date()
            if date > dt.datetime.now().date():
                day, month, year = text.split()
                date = dt.datetime.strptime(
                    f"{day} {month} 19{year}", "%d %m %Y"
                ).date()
            self.cleaned_data["date"] = date
        else:
            self.cleaned_data["date"] = None
        return self.cleaned_data
