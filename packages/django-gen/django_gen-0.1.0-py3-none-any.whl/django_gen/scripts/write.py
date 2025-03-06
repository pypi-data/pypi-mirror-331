import django_gen.templates as templates
from .rewriting import rewrite_middleware


def write_deployment(project_name, **kwargs):
    requirements = """Django\ndjango-environ"""
    setup_cfg = ""
    database = kwargs.get("database")
    use_drf = kwargs.get("use_drf", False)
    use_jwt = kwargs.get("use_jwt", False)
    use_black = kwargs.get("use_black", False)
    use_docker = kwargs.get("use_docker", False)
    use_flake8 = kwargs.get("use_flake8", False)
    use_templates = kwargs.get("use_templates", False)
    use_whitenoise = kwargs.get("use_whitenoise", False)
    use_debug_toolbar = kwargs.get("use_debug_toolbar", False)

    apps = []
    if use_drf:
        apps.append("rest_framework")
        apps.append("drf_yasg")
        apps.append("corsheaders")
    if use_jwt:
        apps.append("rest_framework_simplejwt")
    if use_debug_toolbar:
        apps.append("debug_toolbar")

    app_section = f"""LOCAL_APPS = ["src.core"]
EXTERNAL_APPS = {apps if apps else "[]"}

INSTALLED_APPS += LOCAL_APPS + EXTERNAL_APPS
"""

    settings = templates.BASE_SETTINGS + app_section
    settings = rewrite_middleware(use_whitenoise, use_drf, use_debug_toolbar, settings)

    if use_templates:
        settings += """\n\nTEMPLATES[0]["DIRS"].append(os.path.join(BASE_DIR, "templates"))"""

    if database == "PostgreSQL":
        settings += templates.POSTGRE_SQL
        requirements += "\npsycopg2"
    if database == "MySQL":
        settings += templates.MY_SQL
        requirements += "\nmysqlclient"
    if database == "SQLite" and use_docker is False:
        settings += templates.SQLite
    if database == "SQLite" and use_docker:
        settings += templates.POSTGRE_SQL
        requirements += "\npsycopg2"

    if use_drf:
        settings += templates.DRF
        settings += templates.SWAGGER
        settings += templates.CORS
        requirements += "\ndjangorestframework"
    if use_jwt:
        settings += templates.JWT
        requirements += "\ndjangorestframework-simplejwt"
    if use_debug_toolbar:
        settings += templates.DDT
        requirements += "\ndjango-debug-toolbar"

    settings += templates.MEDIA_SETTINGS
    if use_whitenoise:
        settings += templates.WHITENOISE
        requirements += "\nwhitenoise"

    if use_flake8:
        requirements += "\nflake8"
        setup_cfg += templates.FLAKE8

    if use_black:
        requirements += "\nblack"
        setup_cfg += templates.BLACK

    with open(f"{project_name}/requirements.txt", "w") as file:
        file.write(requirements)

    with open(f"{project_name}/setup.cfg", "w") as file:
        file.write(setup_cfg)

    return settings
