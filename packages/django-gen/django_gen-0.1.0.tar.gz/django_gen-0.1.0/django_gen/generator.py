import os
import sys
import shutil

from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress

import django_gen.scripts as scripts
import django_gen.templates as templates


def project_generator(**kwargs):
    console = Console()
    project_name = kwargs.pop("project_name", "new_project").strip()

    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]🔨 Loyiha tayyorlanmoqda...", total=8)

            os.makedirs(project_name, exist_ok=True)  # add project folder
            progress.update(task, advance=1)

            os.system(f"cd {project_name} && django-admin startproject config .")  # make project
            progress.update(task, advance=1)

            python_cmd = sys.executable
            os.system(f"cd {project_name}/ && mkdir src && cd src/ && {python_cmd} ../manage.py startapp core")
            progress.update(task, advance=1)

            if kwargs.get("use_templates"):
                os.makedirs(f"{project_name}/templates", exist_ok=True)
                open(f"{project_name}/templates/base.html", "w").close()
            progress.update(task, advance=1)

            scripts.make_files(project_name)
            progress.update(task, advance=1)

            scripts.rewrite_files(project_name, **kwargs)
            progress.update(task, advance=1)

            with open(f"{project_name}/config/settings/deployment.py", "w") as file:
                file.write(scripts.write_deployment(project_name, **kwargs))
            progress.update(task, advance=1)

            with open(f"{project_name}/manage.py", "w") as file:
                file.write(templates.MANAGE_PY)
            progress.update(task, advance=1)

        console.print(f"\n[bold green]🏁 \"{project_name.upper()}\" loyihasi tayyor bo‘ldi![/]\n")

    except Exception as e:
        console.print(
            Panel(
                f"❌ [red]Xatolik yuz berdi![/]\n\n[bold yellow]{e}[/]", title="⚠️ Xatolik", border_style="red"
            )
        )
