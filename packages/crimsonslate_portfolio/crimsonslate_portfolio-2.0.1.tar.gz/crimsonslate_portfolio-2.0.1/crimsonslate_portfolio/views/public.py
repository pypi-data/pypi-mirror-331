from django.conf import settings
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from crimsonslate_portfolio.forms import PortfolioAuthenticationForm


class ContactView(TemplateView):
    content_type = "text/html"
    extra_context = {"profile": settings.PORTFOLIO_PROFILE, "title": "Contact"}
    http_method_names = ["get", "post"]
    partial_template_name = "portfolio/partials/_contact.html"
    template_name = "portfolio/contact.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)


class LoginView(LoginViewBase):
    content_type = "text/html"
    extra_context = {"title": "Login", "profile": settings.PORTFOLIO_PROFILE}
    http_method_names = ["get", "post"]
    template_name = "portfolio/login.html"
    partial_template_name = "portfolio/partials/_login.html"
    success_url = reverse_lazy("list files")
    redirect_authenticated_user = True
    form_class = PortfolioAuthenticationForm

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)


class LogoutView(LogoutViewBase):
    content_type = "text/html"
    extra_context = {"title": "Logout", "profile": settings.PORTFOLIO_PROFILE}
    http_method_names = ["get", "post"]
    template_name = "portfolio/logout.html"
    partial_template_name = "portfolio/partials/_logout.html"
    success_url = reverse_lazy("portfolio gallery")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)
