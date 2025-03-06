from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm

from crimsonslate_portfolio.models import Media
from crimsonslate_portfolio.validators import validate_media_file_extension


class PortfolioAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].widget.attrs.update(
                {"class": "p-2 rounded", "placeholder": name.title()}
            )


class MediaUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_media_file_extension])


class MediaCreationForm(ModelForm):
    class Meta:
        model = Media
        fields = [
            "source",
            "thumb",
            "title",
            "subtitle",
            "desc",
            "is_hidden",
            "categories",
            "date_created",
        ]


class MediaEditForm(ModelForm):
    class Meta:
        model = Media
        fields = [
            "source",
            "thumb",
            "title",
            "subtitle",
            "desc",
            "is_hidden",
            "categories",
            "date_created",
        ]
