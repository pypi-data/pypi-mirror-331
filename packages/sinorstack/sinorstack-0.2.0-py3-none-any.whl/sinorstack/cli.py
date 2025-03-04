import typer
from copier import run_copy
from pathlib import Path

cli = typer.Typer()


@cli.command()
def new(name: str):
    """Создает новый проект Sinorstack"""
    typer.echo(f"🔥🔥 Генерация {name}... 🔥🔥")
    template_dir = Path(__file__).parent / "_template"
    run_copy(str(template_dir), str(Path.cwd() / name))
    typer.echo("✅ Готово!")


if __name__ == "__main__":
    cli()
