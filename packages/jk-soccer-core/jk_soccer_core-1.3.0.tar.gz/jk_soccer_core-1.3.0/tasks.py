from invoke import task, Exit
import os
import shutil
import fnmatch


@task(aliases=["c"])
def clean(ctx):
    """Clean up build artifacts and temporary files."""
    patterns = [
        "build",
        "dist",
        "*.egg-info",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "junit.xml",
        ".coverage",
    ]

    for pattern in patterns:
        for path in ctx.run(f'find . -name "{pattern}"', hide=True).stdout.splitlines():
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


@task(aliases=["b"])
def build(ctx):
    """Build the project using uv."""
    ctx.run("uv build")


@task(aliases=["m"])
def mypy(ctx):
    """Run mypy for static type checking."""
    ctx.run("mypy src/jk_soccer_core")


@task(aliases=["l"], pre=[mypy])
def lint(ctx):
    """Lint the project using ruff."""
    ctx.run("ruff check .")


@task(aliases=["f"])
def fmt(ctx):
    """Format the project using ruff."""
    ctx.run("ruff format  .")


@task(aliases=["t"])
def test(ctx):
    """Run tests using pytest."""
    ctx.run("uv run pytest -v --cov=src tests/unit --junitxml=junit.xml")


@task(aliases=["j"])
def jsonlint(ctx):
    """Lint JSON files using jsonlint."""
    failed_files = []
    for root, dirnames, filenames in os.walk("."):
        if "node_modules" in dirnames:
            dirnames.remove("node_modules")
        if ".venv" in dirnames:
            dirnames.remove(".venv")
        for filename in fnmatch.filter(filenames, "*.json"):
            json_file = os.path.join(root, filename)

            try:
                ctx.run(f"jsonlint -c {json_file}", hide=True)
                print(f"Passed verification: {json_file}")
            except Exception:
                print(f"Failed verification: {json_file}")
                failed_files.append(json_file)

    if failed_files:
        raise Exit(code=1)


@task(aliases=["i"])
def install(ctx):
    # Install Python dependencies using pip
    ctx.run("uv sync --all-extras --dev")
