import django_gen.templates as templates


def rewrite_middleware(use_whitenoise, use_drf, use_debug_toolbar, settings):
    middleware_list = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    if use_whitenoise:
        i = middleware_list.index('django.middleware.security.SecurityMiddleware')
        middleware_list.insert(i + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

    if use_drf:
        middleware_list.insert(0, "corsheaders.middleware.CorsMiddleware")

    if use_debug_toolbar:
        i = middleware_list.index('django.contrib.sessions.middleware.SessionMiddleware')
        middleware_list.insert(i + 1, "debug_toolbar.middleware.DebugToolbarMiddleware")

    settings += "MIDDLEWARE = [\n    " + ",\n    ".join(f'"{mw}"' for mw in middleware_list) + "\n]"
    return settings


def rewrite_urls(use_drf=False, use_jwt=False, use_debug_toolbar=False):
    imports = [
        "from django.contrib import admin",
        "from django.urls import path, include",
        "",
        "from django.conf import settings",
        "from django.conf.urls.static import static",
    ]

    urlpatterns = [
        "",
        "urlpatterns = [",
        "    path('admin/', admin.site.urls),",
        "    #path('', include('src.api.include_routers')),",
    ]

    if use_drf:
        imports.append("from src.shared.drf_yasg import yasg_schema_view")
        urlpatterns += [
            "    path('api-auth/', include('rest_framework.urls')),",
            "    path('docs/', yasg_schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),",
            "    path('swagger/', yasg_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),",
        ]

    if use_jwt:
        imports.append("from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView")
        urlpatterns += [
            "    path('api/auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),",
            "    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),",
        ]

    urlpatterns += ["]"]

    urlpatterns += [
        "urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)",
        "urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)",
    ]

    if use_debug_toolbar:
        urlpatterns.append("")
        urlpatterns.append("import debug_toolbar")
        urlpatterns.append("urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))")

    return "\n".join(imports + urlpatterns)


def rewrite_files(project_name, **kwargs):
    use_docker = kwargs.get("use_docker", False)

    with open(f"{project_name}/src/core/apps.py", "w") as file:
        file.write(templates.APPS_PY)

    with open(f"{project_name}/src/core/models/base.py", "w") as file:
        file.write(templates.BASE_MODEL)

    with open(f"{project_name}/src/api/include_routers.py", "w") as file:
        file.write(templates.INCLUDE_ROUTERS)

    with open(f"{project_name}/src/apps/serializers/base.py", "w") as file:
        file.write(templates.BASE_SERIALIZER)

    if kwargs.get("templates", False):
        with open(f"{project_name}/templates/base.html", "w") as file:
            file.write(templates.BASE_TEMPLATE)

    with open(f"{project_name}/config/urls.py", "w") as file:
        file.write(
            rewrite_urls(
                kwargs.get("use_drf", False),
                kwargs.get("use_jwt", False),
                kwargs.get("use_debug_toolbar", False)
            )
        )

    with open(f"{project_name}/src/shared/drf_yasg.py", "w") as file:
        file.write(templates.DRF_YASG)

    env = templates.ENV_EXAMPLE
    env += "\nDOCKER=1" if use_docker else ""
    if kwargs.get("database") != "SQLite":
        env += templates.DB_ENV_EXAMPLE

    with open(f"{project_name}/.env.dev", "w") as file:
        file.write(env)

    with open(f"{project_name}/.env.example", "w") as file:
        file.write(env)

    with open(f"{project_name}/.gitignore", "w") as file:
        file.write(templates.GITIGNORE)

    if use_docker:
        with open(f"{project_name}/Dockerfile", "w") as file:
            file.write(templates.DOCKERFILE)

        with open(f"{project_name}/docker-compose.yml", "w") as file:
            file.write(templates.DOCKER_COMPOSE)

        with open(f"{project_name}/entrypoint.sh", "w") as file:
            file.write(templates.ENTRYPOINT)
