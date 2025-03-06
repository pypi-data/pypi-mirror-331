from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
    ListView,
)

from crimsonslate_portfolio.forms import MediaCreateForm, MediaUpdateForm
from crimsonslate_portfolio.models import Media
from crimsonslate_portfolio.views.mixins import (
    HtmxTemplateResponseMixin,
    PortfolioProfileMixin,
    PortfolioSingleObjectMixin,
    PortfolioMultipleObjectMixin,
)


class MediaUploadView(
    LoginRequiredMixin, PortfolioProfileMixin, HtmxTemplateResponseMixin, TemplateView
):
    http_method_names = ["get"]
    extra_context = {"title": "Upload", "class": "bg-violet-300"}
    template_name = "portfolio/media/upload.html"
    partial_template_name = "portfolio/media/partials/_upload.html"
    login_url = reverse_lazy("login")
    raise_exception = False
    permission_denied_message = "Please login and try again."


class MediaUploadSuccessView(
    HtmxTemplateResponseMixin, PortfolioProfileMixin, TemplateView
):
    http_method_names = ["get"]
    extra_context = {"title": "Success", "class": ""}
    template_name = "portfolio/media/upload_success.html"
    partial_template_name = "portfolio/media/partials/_upload_success.html"


class MediaDeleteView(
    HtmxTemplateResponseMixin,
    PortfolioSingleObjectMixin,
    PortfolioProfileMixin,
    DeleteView,
):
    model = Media
    template_name = "portfolio/media/delete.html"
    partial_template_name = "portfolio/media/partials/_delete.html"
    http_method_names = ["get", "post"]


class MediaCreateView(HtmxTemplateResponseMixin, PortfolioProfileMixin, CreateView):
    form_class = MediaCreateForm
    http_method_names = ["get", "post"]
    model = Media
    partial_template_name = "portfolio/media/partials/_create.html"
    template_name = "portfolio/media/create.html"


class MediaUpdateView(
    HtmxTemplateResponseMixin,
    PortfolioSingleObjectMixin,
    PortfolioProfileMixin,
    UpdateView,
):
    form_class = MediaUpdateForm
    http_method_names = ["get", "post"]
    model = Media
    partial_template_name = "portfolio/media/partials/_update.html"
    template_name = "portfolio/media/update.html"


class MediaDetailView(
    HtmxTemplateResponseMixin,
    PortfolioSingleObjectMixin,
    PortfolioProfileMixin,
    DetailView,
):
    http_method_names = ["get"]
    model = Media
    partial_template_name = "portfolio/media/partials/_detail.html"
    queryset = Media.objects.all()
    template_name = "portfolio/media/detail.html"


class MediaGalleryView(
    HtmxTemplateResponseMixin,
    PortfolioMultipleObjectMixin,
    PortfolioProfileMixin,
    ListView,
):
    allow_empty = True
    extra_context = {"title": "Gallery"}
    http_method_names = ["get"]
    model = Media
    ordering = "date_created"
    paginate_by = 12
    partial_template_name = "portfolio/media/partials/_gallery.html"
    queryset = Media.objects.all()
    template_name = "portfolio/media/gallery.html"


class MediaSearchView(
    HtmxTemplateResponseMixin,
    PortfolioMultipleObjectMixin,
    PortfolioProfileMixin,
    ListView,
):
    allow_empty = True
    extra_context = {"title": "Search"}
    http_method_names = ["get"]
    model = Media
    ordering = "name"
    paginate_by = 12
    partial_template_name = "portfolio/media/partials/_search.html"
    queryset = Media.objects.all()
    template_name = "portfolio/media/search.html"
