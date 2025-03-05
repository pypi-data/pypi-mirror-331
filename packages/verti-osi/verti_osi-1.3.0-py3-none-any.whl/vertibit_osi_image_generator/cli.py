import typer
from .language_scanner import main_language_scanner
from .file_configuration import extract_images
from .docker_file_generator import main_docker_file_generator
from .generate_docker_image import build_docker_image
import os


app = typer.Typer()


@app.command()
def create(root_directory: str = typer.Option('.', help="The projects root directory"), source_directory: str = typer.Option('.', help="The projects source code directory."), image_name: str = typer.Option(..., help="The image name for the generated image."), daemon: str = typer.Option('docker', help="The daemon to be used."), output: str = typer.Option('', help="The generated image output type.(supports tar, registry pushing, and standard image generation)"), delete_generated_dockerfile: str = typer.Option('False', help="Delete the generated dockerfile image"), run_generated_image: str = typer.Option('False', help="Run the generated docker image.")):
    """
    Generate a container image.
    """
    language_info = main_language_scanner(root_directory)
    images = extract_images(language_info["language"])

    docker_file_content = main_docker_file_generator(
        language_info=language_info, images=images, source_directory=source_directory, root_directory=root_directory)

    typer.echo(f"Identified language: {language_info['language']}")
    typer.echo(f"Identified language images: {images}")

    # Ensure the 'tmp' directory exists
    os.makedirs("tmp", exist_ok=True)

    # Save to a file
    with open("tmp/Dockerfile", "w") as f:
        f.write(docker_file_content)

    build_docker_image(daemon=daemon, image_name=image_name, container_file='tmp/Dockerfile',
                       build_context=root_directory, output=output, delete_generated_dockerfile=delete_generated_dockerfile, run_generated_image=run_generated_image)


if __name__ == "__main__":
    app()
