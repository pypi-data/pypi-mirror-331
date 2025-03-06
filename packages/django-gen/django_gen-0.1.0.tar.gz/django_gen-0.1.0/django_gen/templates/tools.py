DRF_YASG = """from drf_yasg import openapi
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view

API_TITLE = 'API doc'
API_DESCRIPTION = 'API documents'

yasg_schema_view = get_schema_view(
    openapi.Info(
        title=API_TITLE,
        default_version='v1',
        description=API_DESCRIPTION,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="example@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_title = "Admin panel"
admin.site.site_header = "Admin panel"
admin.site.index_title = "Admin panel"
"""

ENV_EXAMPLE = """DEBUG=1
SECRET_KEY=django_secret_key
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
"""

DB_ENV_EXAMPLE = """
DB_PASS=123
DB_PORT=5432
DB_USER=server
DB_NAME=db_name
DB_HOST=localhost"""

GITIGNORE = """venv
.idea
.idea/
.env.dev

# Python bytecode files
__pycache__/
*.py[cod]

# Django migrations
*/migrations/
*.pyc
*.pyo

db.sqlite3
*.sqlite3

/media/
staticfiles/
"""

BLACK = """
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    | migrations  # Django migrations
    | venv        # Virtual environment
    | .venv       # Alternativ virtual env
    | build       # Build papka
    | dist        # Distributive fayllar
    | __pycache__ # Kesh fayllar
)/
'''

[isort]
profile = black
"""

FLAKE8 = """[flake8]
max-line-length = 100
exclude = .git, __pycache__, venv, .venv, migrations
max-complexity = 10
select = C,E,F,W,B,B950
ignore = E203, E501, W503
"""
