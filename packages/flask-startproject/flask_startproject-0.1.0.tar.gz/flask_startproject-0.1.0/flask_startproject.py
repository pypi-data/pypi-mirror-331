#!/usr/bin/env python3

import os
import json
import argparse
import subprocess
import platform

dependencies = {
    "auth": ["Flask-Security-Too"],
    "db": ["Flask-SQLAlchemy"],
    "migrate": ["Flask-Migrate"],
    "cache": ["Flask-Caching"],
    "mail": ["Flask-Mailman"],
    "validation": ["Marshmallow"],
    "jobs": ["Celery"]
}

def read_config_file(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Config file '{filename}' not found")

    try:
        with open(filename, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON file '{filename}': {e}")

def main():
    parser = argparse.ArgumentParser(
        prog="Flask Start Project",
        description="Flask project initializer"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument("-d", "--deps", action="store", help="Specifies the dependencies. Ex: (auth,db...)")
    parser.add_argument("-f", "--from-file", help="Load dependencies from a config file (JSON)")
    parser.add_argument("--all-deps", action="store_true", help="Install all dependencies")
    parser.add_argument("--git-init", action="store_true", help="Initialize git repository")
    parser.add_argument("--requirements", action="store_true", help="Create requirements file")

    args = parser.parse_args()

    config = read_config_file(args.from_file) if args.from_file else dependencies

    project_dir = os.path.abspath(args.name)
    venv_path = os.path.join(project_dir, "venv")

    print(f"Creating project directory: {project_dir}")
    os.makedirs(project_dir, exist_ok=True)

    print("Creating virtual environment...")
    subprocess.run(["python3", "-m", "venv", venv_path], check=True)

    system = platform.system().lower()
    if system == "windows":
        pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        pip_exec = os.path.join(venv_path, "bin", "pip")

    libs = ["Flask"]
    deps = args.deps.split(",") if args.deps else []
    if args.all_deps:
        deps = list(config.keys())

    for dep in deps:
        libs.extend(config.get(dep, []))

    if libs:
        print("Installing dependencies...")
        subprocess.run([pip_exec, "install"] + libs, check=True)

    if args.requirements:
        print("Generating requirements.txt...")
        with open(os.path.join(project_dir, "requirements.txt"), "w") as req_file:
            subprocess.run([pip_exec, "freeze"], stdout=req_file, check=True)

    if args.git_init:
        print("Initializing Git repository...")
        subprocess.run(["git", "init"], cwd=project_dir, check=True)

    app_template = """
    from flask import Flask
    
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Hello, Flask!"

    if __name__ == "__main__":
        app.run(debug=True)
    """

    with open(os.path.join(project_dir, "app.py"), "w") as f:
        f.write(app_template)

    print("Created app.py with a basic Flask setup.")
    print("Flask project setup completed!")

if __name__ == "__main__":
    main()
