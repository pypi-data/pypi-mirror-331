# type: ignore
import os
from click import prompt
from invoke import task
import re
import time


def get_version_from_dist():
    dist_files = os.listdir("dist")
    for filename in dist_files:
        match = re.match(r"rox_septentrio-(\d+\.\d+\.\d+(\.dev\d+)?)", filename)
        if match:
            return match.group(1)
    raise ValueError("Version not found in dist folder")


@task
def clean(ctx):
    """
    Remove all files and directories that are not under version control to ensure a pristine working environment.
    Use caution as this operation cannot be undone and might remove untracked files.

    """

    ctx.run("git clean -nfdx")

    if (
        prompt(
            "Are you sure you want to remove all untracked files? (y/n)", default="n"
        )
        == "y"
    ):
        ctx.run("git clean -fdx")


@task
def lint(ctx):
    """
    Perform static analysis on the source code to check for syntax errors and enforce style consistency.
    """
    ctx.run("ruff check src tests")
    ctx.run("mypy src")


@task
def test(ctx):
    """
    Run tests with coverage reporting to ensure code functionality and quality.
    """
    ctx.run("pytest --cov=src --cov-report term-missing tests")


@task
def ci(ctx):
    """
    run ci locally in a fresh container

    """
    t_start = time.time()
    # get script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        ctx.run(f"docker run --rm -v {script_dir}:/workspace roxauto/python-ci")
    finally:
        t_end = time.time()
        print(f"CI run took {t_end - t_start:.1f} seconds")


@task
def build_package(ctx):
    """
    Build package in docker container.
    """

    ctx.run("rm -rf dist")
    t_start = time.time()
    # get script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        ctx.run(
            f"docker run --rm -v {script_dir}:/workspace roxauto/python-ci /scripts/build.sh"
        )
    finally:
        t_end = time.time()
        print(f"CI run took {t_end - t_start:.1f} seconds")


@task
def release(ctx):
    """publish package to pypi"""
    script_dir = os.path.dirname(os.path.realpath(__file__))

    token = os.getenv("PYPI_TOKEN")
    if not token:
        raise ValueError("PYPI_TOKEN environment variable is not set")

    ctx.run(
        f"docker run --rm -e PYPI_TOKEN={token} -v {script_dir}:/workspace roxauto/python-ci /scripts/publish.sh"
    )


@task
def build_image(c, push=False):
    """build docker image, optionally push it to GitLab registry"""
    # Ensure the script stops on errors and undefined variables
    IMG = "registry.gitlab.com/roxautomation/components/septentrio-gps"
    TAG = get_version_from_dist()
    ARCH = "linux/amd64,linux/arm64,linux/arm/v7"
    print(f"Building image {IMG}:{TAG}")

    # copy dist folder to docker folder
    c.run("rm -rf docker/dist")
    c.run("cp -r dist docker/")

    c.run("set -o errexit")
    c.run("set -o nounset")

    # Check that dist folder exists
    if not os.path.exists("dist"):
        print("dist folder does not exist. Building...")
        c.run("invoke build")
        return

    # Build image locally and upload it to GitLab
    c.run("docker run --rm --privileged multiarch/qemu-user-static --reset -p yes")

    # Check if the builder already exists
    result = c.run("docker buildx inspect mybuilder", warn=True, hide=True)
    if result.ok:
        print("Builder 'mybuilder' already exists. Removing it...")
        c.run("docker buildx rm mybuilder")

    # Create and use a new builder instance
    c.run("docker buildx create --name mybuilder --use")
    c.run("docker buildx inspect --bootstrap")

    # Build the image
    push_option = "--push" if push else ""
    c.run(
        f"docker buildx build --platform {ARCH} "
        f"-t {IMG}:{TAG} "
        f"-t {IMG}:latest"
        f" {push_option} ./docker"
    )
