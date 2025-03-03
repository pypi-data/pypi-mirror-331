import typer
import os
import pkg_resources
import psutil
import re
import subprocess
import time


def extract_label_value(text, key="label"):
    pattern = rf"'{key}'\s*:\s*'([^']+)'"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


def print_success(message: str):
    typer.echo(typer.style(message, fg=typer.colors.GREEN))


def print_error(message: str):
    typer.echo(typer.style(message, fg=typer.colors.RED))


def print_success_bold(message: str):
    typer.echo(typer.style(message, fg=typer.colors.GREEN, bold=True))


def print_neutral(message: str):
    typer.echo(typer.style(message, fg=typer.colors.BLUE))


def sanitize_model_name(model: str):
    return model.replace("/", "_")


def unsanitize_model_name(model: str):
    return model.replace("_", "/")


def get_package_dir() -> str:
    return pkg_resources.resource_filename("textforge", "")


def get_models_dir():
    os.makedirs(os.path.join(get_package_dir(), "data", "models"), exist_ok=True)
    return os.path.join(get_package_dir(), "data", "models")


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def install_ollama(model="llama3.1:8b-instruct-q4_0"):
    subprocess.run("apt-get update && apt-get upgrade -y", shell=True)
    subprocess.run(["apt-get install lshw"], shell=True)
    subprocess.run(["curl https://ollama.ai/install.sh | sh"], shell=True)
    serve_process = subprocess.Popen(["ollama serve"], shell=True)
    time.sleep(5)
    subprocess.run([f"ollama pull {model}"], shell=True)
    print_success("OLLAMA installed successfully")
