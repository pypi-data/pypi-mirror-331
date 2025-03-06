import os
import shutil

all_folders = [
    "config/settings", "src/api", "src/apps", "src/apps/serializers",
    "src/apps/views", "src/apps/urls", "src/core/models", "src/core/admin", "src/shared"
]

all_files = [
    "config/settings/deployment.py", "src/core/models/base.py", "src/apps/serializers/base.py",
    ".env.dev", ".env.example", ".gitignore"
]

remove_files = [
    "src/core/models.py", "src/core/tests.py", "src/core/views.py", "src/core/admin.py"
]


def make_files(project_name):
    project_path = os.path.abspath(project_name)

    for folder in all_folders:
        folder_path = os.path.join(project_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        open(os.path.join(folder_path, "__init__.py"), "w").close()

    for file in remove_files:
        file_path = os.path.join(project_path, file)
        if os.path.exists(file_path):
            os.remove(file_path)

    for file in all_files:
        file_path = os.path.join(project_path, file)
        open(file_path, "w").close()

    settings_dir = os.path.join(project_path, "config", "settings")
    os.makedirs(settings_dir, exist_ok=True)

    old_settings_path = os.path.join(project_path, "config", "settings.py")
    new_settings_path = os.path.join(settings_dir, "base.py")

    if os.path.exists(old_settings_path):
        shutil.move(old_settings_path, new_settings_path)
