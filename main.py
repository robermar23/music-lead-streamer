import typer
import importlib
import pygame
import time
import threading
from pathlib import Path
from util import get_shows, setup_display, SHOWS_PATH

app = typer.Typer()

@app.command()
def list_shows():
    """
    List all available shows.
    """
    shows = get_shows()
    if not shows:
        typer.echo("No available shows found.")
    else:
        typer.echo("Available shows:")
        for show in shows:
            typer.echo(f"- {show}")


@app.command()
def run(
    show: str,
    display: str = typer.Argument(":0", help="Display to run the show on (e.g., ':0')"),
    video_driver: str = typer.Argument("x11", help="Video driver to use (e.g., 'x11')"),
    screen_width: int = typer.Argument(800, help="Screen width (e.g., 800)"),
    screen_height: int = typer.Argument(480, help="Screen height (e.g., 480)"),
    samplerate: int = typer.Argument(44100, help="Sample rate for the audio stream"),
    channels: int = typer.Argument(2, help="Number of audio channels"),
    device_index: int = typer.Argument(1, help="Index of the audio device to use"),
    blocksize: int = typer.Argument(1024, help="Block size for audio processing"),
    latency: float = typer.Argument(0.1, help="Audio stream latency"),
):
    """
    Run a specific show by name.
    """
    # Set up display
    screen = setup_display(display, video_driver, screen_width, screen_height)
    pygame.display.set_caption(f"Running Show: {show}")

    # Shared audio settings
    audio_settings = (samplerate, channels, device_index, blocksize, latency)

    try:
        # Import the selected show
        show_module = importlib.import_module(f"show.{show}")

        # Initialize the show
        if hasattr(show_module, "initialize"):
            show_module.initialize(audio_settings, screen)
        else:
            typer.echo(f"Error: Show '{show}' does not have an 'initialize()' function.")
            raise typer.Exit(code=1)

        # Main loop
        typer.echo(f"Running show '{show}'. Press Ctrl+C to quit.")
        clock = pygame.time.Clock()
        running = True
        while running:
            # Render the current frame
            if hasattr(show_module, "render_step"):
                show_module.render_step(screen)
            else:
                typer.echo(f"Error: Show '{show}' does not have a 'render_step()' function.")
                break

            # Handle quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            clock.tick(30)  # Limit frame rate to 30 FPS

    except KeyboardInterrupt:
        typer.echo("Exiting show.")
    except Exception as e:
        typer.echo(f"Error running show '{show}': {e}")
    finally:
        # Cleanup resources
        if hasattr(show_module, "cleanup"):
            show_module.cleanup()
        pygame.quit()

@app.command()
def rotate(
    display: str = typer.Argument(..., help="Display to run the shows on (e.g., ':0')"),
    video_driver: str = typer.Argument(..., help="Video driver to use (e.g., 'x11')"),
    screen_width: int = typer.Argument(..., help="Screen width (e.g., 800)"),
    screen_height: int = typer.Argument(..., help="Screen height (e.g., 480)"),
    samplerate: int = typer.Argument(44100, help="Sample rate for the audio stream"),
    channels: int = typer.Argument(2, help="Number of audio channels"),
    device_index: int = typer.Argument(None, help="Index of the audio device to use"),
    blocksize: int = typer.Argument(1024, help="Block size for audio processing"),
    latency: float = typer.Argument(0.1, help="Audio stream latency"),
    timer: int = typer.Argument(30, help="Time in seconds before switching to the next show"),
):
    """Rotate through each show based on a timer. Press SPACEBAR to skip to the next show."""
    # List available shows
    shows = list_shows()
    if not shows:
        typer.echo("No shows available to rotate.")
        raise typer.Exit(code=1)

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Show Rotator")

    # Shared audio settings
    audio_settings = (samplerate, channels, device_index, blocksize, latency)

    current_index = 0
    clock = pygame.time.Clock()
    start_time = time.time()
    running = True

    # Load and initialize the first show
    show_module = None

    def load_show(index):
        """Load and initialize the current show."""
        nonlocal show_module
        if show_module and hasattr(show_module, "cleanup"):
            show_module.cleanup()  # Clean up the previous show
        show_name = shows[index]
        show_module = importlib.import_module(f"show.{show_name}")
        if hasattr(show_module, "initialize"):
            show_module.initialize(audio_settings)

    load_show(current_index)

    typer.echo("Press SPACEBAR to skip to the next show.")

    while running:
        try:
            elapsed_time = time.time() - start_time

            # Check for show switch
            if elapsed_time >= timer:
                current_index = (current_index + 1) % len(shows)
                load_show(current_index)
                start_time = time.time()

            # Render the current show
            if hasattr(show_module, "render_step"):
                show_module.render_step(screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    current_index = (current_index + 1) % len(shows)
                    load_show(current_index)
                    start_time = time.time()

            clock.tick(30)  # Limit frame rate to 30 FPS

        except Exception as e:
            typer.echo(f"Error running show '{shows[current_index]}': {e}")
            break

    if show_module and hasattr(show_module, "cleanup"):
        show_module.cleanup()
    pygame.quit()


if __name__ == "__main__":
    app()

