import os
import click
import shutil
from rich.prompt import Confirm
from rich.console import Console
from django_gen.generator import project_generator


@click.command()
@click.argument("project_name")
def main(project_name):
    console = Console()

    if os.path.exists(project_name):
        console.print(f"[bold yellow]⚠️ '{project_name}' papkasi allaqachon mavjud![/]")

        if Confirm.ask(f"[bold]Uni o‘chirib yangisini yaratishni xohlaysizmi?[/]"):
            shutil.rmtree(project_name)
            console.print(f"[bold green]✅ '{project_name}' papkasi o‘chirildi!")

    console.print(f"\n[bold cyan]🎯 \"{str(project_name).upper()}\" loyihasini yaratamiz...[/]\n")

    # Asosiy konfiguratsiyalar
    console.print("\n[bold cyan]📌 Loyihaning asosiy komponentlarini tanlang:[/]\n")
    use_drf = Confirm.ask("🖥 Django REST Framework (DRF) kerakmi?")
    use_templates = Confirm.ask("🎨 Django Templates ishlatiladimi?")
    use_jwt = Confirm.ask("🔐 JWT Authentication kerakmi?")
    use_docker = Confirm.ask("🐳 Docker orqali ishga tushirasizmi?")

    # Backend texnologiyalar
    console.print("\n[bold cyan]⚙️ Backend texnologiyalar:[/]\n")
    # use_celery = Confirm.ask("⚡ Celery (fon vazifalar) kerakmi?")
    # use_redis = Confirm.ask("🛢 Redis kerakmi?")
    use_whitenoise = Confirm.ask("📁 Whitenoise (statik fayllar) kerakmi?")

    # Database tanlash
    console.print("\n[bold cyan]🗄 Qaysi database-ni ishlatmoqchisiz?[/]\n")
    options = ["PostgreSQL", "MySQL", "SQLite"]

    for i, option in enumerate(options, start=1):
        console.print(f"[bold yellow]{i}.[/] {option}")

    choice = input("\n>>>: ").strip()
    db_choice = options[int(choice) - 1] if choice in ["1", "2", "3"] else "SQLite"

    # Qo‘shimcha vositalar
    console.print("\n[bold cyan]🛠 Qo‘shimcha vositalarni tanlang:[/]\n")
    use_debug_toolbar = Confirm.ask("🛠 Django Debug Toolbar o‘rnatilsinmi?")
    use_black = Confirm.ask("🎨 Black formatter o‘rnatilsinmi?")
    use_flake8 = Confirm.ask("🧹 Flake8 linter o‘rnatilsinmi?")

    # Tanlangan sozlamalarni chiqarish
    console.print("\n[bold green]✅ Siz tanlagan sozlamalar:[/]")
    console.print(f"   - 🗄 Database: [yellow]{db_choice}[/]")
    if use_drf: console.print("   - 🖥 Django REST Framework (DRF): [green]Ha[/]")
    if use_templates: console.print("   - 🎨 Django Templates: [green]Ha[/]")
    if use_jwt: console.print("   - 🔐 JWT Authentication: [green]Ha[/]")
    if use_docker: console.print("   - 🐳 Docker: [green]Ha[/]")
    # if use_celery: console.print("   - ⚡ Celery: [green]Ha[/]")
    # if use_redis: console.print("   - 🛢 Redis: [green]Ha[/]")
    if use_whitenoise: console.print("   - 📁 Whitenoise: [green]Ha[/]")
    if use_debug_toolbar: console.print("   - 🛠 Django Debug Toolbar: [green]Ha[/]")
    if use_black: console.print("   - 🎨 Black formatter: [green]Ha[/]")
    if use_flake8: console.print("   - 🧹 Flake8 linter: [green]Ha[/]")

    # **Loyihani tayorlash**
    project_generator(
        project_name=project_name,
        use_drf=use_drf,
        use_templates=use_templates,
        use_jwt=use_jwt,
        use_docker=use_docker,
        # use_celery=use_celery,
        # use_redis=use_redis,
        use_whitenoise=use_whitenoise,
        use_debug_toolbar=use_debug_toolbar,
        use_black=use_black,
        use_flake8=use_flake8,
        database=db_choice
    )


if __name__ == "__main__":
    main()
