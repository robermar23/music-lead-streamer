import typer
import importlib
import pygame
import time
import threading
from pathlib import Path
from util import get_shows, setup_display, SHOWS_PATH

app = typer.Typer()

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
    Run a show by its name (module in the "show" folder).
    """
    show_module_path = SHOWS_PATH / f"{show}.py"
    if not show_module_path.exists():
        typer.echo(f"Error: Show '{show}' not found.")
        raise typer.Exit(code=1)

    try:
        # Dynamically import the selected show module
        show_module = importlib.import_module(f"show.{show}")
        
        # Call the main function in the module if it exists
        if hasattr(show_module, "main"):
            # Call the 'main' function with all the required arguments
            show_module.main(
                display,
                video_driver,
                screen_width,
                screen_height,
                samplerate,
                channels,
                device_index,
                blocksize,
                latency,
            )
        else:
            typer.echo(f"Error: Show '{show}' does not have a 'main' function.")
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"Error loading show '{show}': {e}")
        raise typer.Exit(code=1)

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
def rotate(
    display: str = typer.Argument(":0", help="Display to run the show on (e.g., ':0')"),
    video_driver: str = typer.Argument("x11", help="Video driver to use (e.g., 'x11')"),
    screen_width: int = typer.Argument(800, help="Screen width (e.g., 800)"),
    screen_height: int = typer.Argument(480, help="Screen height (e.g., 480)"),
    samplerate: int = typer.Argument(44100, help="Sample rate for the audio stream"),
    channels: int = typer.Argument(2, help="Number of audio channels"),
    device_index: int = typer.Argument(1, help="Index of the audio device to use"),
    blocksize: int = typer.Argument(1024, help="Block size for audio processing"),
    latency: float = typer.Argument(0.1, help="Audio stream latency"),
    timer: int = typer.Argument(10, help="Time in seconds before switching to the next show"),
):
    """
    Rotate through each show based on a timer. Press SPACEBAR to skip to the next show.
    """
    shows = get_shows()
    if not shows:
        typer.echo("No shows available to rotate.")
        raise typer.Exit(code=1)

    def run_show(show):
        """
        Dynamically import and run a show.
        """
        typer.echo(f"Running show: {show}")
        try:
            show_module = importlib.import_module(f"show.{show}")
            if hasattr(show_module, "main"):
                show_module.main(
                    display,
                    video_driver,
                    screen_width,
                    screen_height,
                    samplerate,
                    channels,
                    device_index,
                    blocksize,
                    latency,
                )
            else:
                typer.echo(f"Error: Show '{show}' does not have a 'main' function.")
        except Exception as e:
            typer.echo(f"Error running show '{show}': {e}")

    # Initialize Pygame for key detection
    # pygame.init()
    # screen = pygame.display.set_mode((1, 1))  # Minimal screen for key input handling
    # pygame.display.set_caption("Show Rotator")
    screen = setup_display(display, video_driver, screen_width, screen_height)

    current_index = 0
    running = True

    def event_listener():
        """
        Listen for SPACEBAR to skip the current show.
        """
        nonlocal current_index, running
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Spacebar pressed 
                        current_index = (current_index + 1) % len(shows)
                        return

    typer.echo("Press SPACEBAR to skip to the next show.")

    try:
        while running:
            start_time = time.time()
            # Run the current show
            show = shows[current_index]

            # Run the show in a separate thread to allow event handling
            thread = threading.Thread(target=run_show, args=(show,))
            thread.start()

            # Wait for the timer or SPACEBAR press
            while time.time() - start_time < timer:
                event_listener()
                if not thread.is_alive():  # Ensure show completes gracefully
                    break

            # Move to the next show
            current_index = (current_index + 1) % len(shows)
    except KeyboardInterrupt:
        typer.echo("Exiting rotation.")
    finally:
        running = False
        pygame.quit()

if __name__ == "__main__":
    app()

