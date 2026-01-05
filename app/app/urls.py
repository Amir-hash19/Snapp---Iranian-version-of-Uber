from rest_framework.authentication import SessionAuthentication
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from account.views import health_check


schema_view = get_schema_view(
    openapi.Info(
        title="Snapp Iranian Version of UBER",
        default_version="v1",
        description="A sample Django project simulating the "
        "Iranian version of Uber, named Snapp, with REST API"
        " endpoints and Swagger documentation.",
        terms_of_service="https://amir-hash19.github.io/",
        contact=openapi.Contact(email="amirhosein.hydri1381@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[SessionAuthentication],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/account/", include("account.urls")),
    path("api/", include("order.urls")),
    path("", health_check, name="health check endpoint"),
    # Only for developer
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
