import typer
import importlib
import pygame
import time
from music_led_streamer.util import get_shows, setup_display, SHOWS_PATH, load_config

app = typer.Typer()

# Global variable to store config path
config_path = None

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

    return shows


@app.command()
def run(
    show: str = typer.Argument("stars", help="Show to run (e.g., 'stars, bubbles, shapes, etc.')"),
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
    show_module = None

    # Shared audio settings
    audio_settings = (samplerate, channels, device_index, blocksize, latency)

    try:
        # Import the selected show
        show_module = importlib.import_module(f"music_led_streamer.show.{show}")

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
    display: str = typer.Argument(":0", help="Display to run the show on (e.g., ':0')"),
    video_driver: str = typer.Argument("x11", help="Video driver to use (e.g., 'x11')"),
    screen_width: int = typer.Argument(800, help="Screen width (e.g., 800)"),
    screen_height: int = typer.Argument(480, help="Screen height (e.g., 480)"),
    samplerate: int = typer.Argument(44100, help="Sample rate for the audio stream"),
    channels: int = typer.Argument(2, help="Number of audio channels"),
    device_index: int = typer.Argument(1, help="Index of the audio device to use"),
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

    screen = setup_display(display, video_driver, screen_width, screen_height)
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
        show_module = importlib.import_module(f"music_led_streamer.show.{show_name}")
        if hasattr(show_module, "initialize"):
            show_module.initialize(audio_settings, screen)

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

def config():
    """Default command function if no command is provided."""
    print("No command provided. Looking for available configuration file...")

    config = load_config(config_path)
    if config:
        print(f"Configuration found: {config}")
        if config["command"] == "run":
            run(show=config["show"], 
                      display=config["display"], 
                      video_driver=config["video_driver"], 
                      screen_width=config["screen_width"], 
                      screen_height=config["screen_height"], 
                      samplerate=config["samplerate"], 
                      channels=config["channels"], 
                      device_index=config["device_index"], 
                      blocksize=config["blocksize"], 
                      latency=config["latency"]
                    )
        elif config["command"] == "rotate":
            rotate(display=config["display"], 
                      video_driver=config["video_driver"], 
                      screen_width=config["screen_width"], 
                      screen_height=config["screen_height"], 
                      samplerate=config["samplerate"], 
                      channels=config["channels"], 
                      device_index=config["device_index"], 
                      blocksize=config["blocksize"], 
                      latency=config["latency"],
                      timer=config["timer"]
                    )
    else:
        print("No configuration found. Will 'run` with defaults...")
        typer.run(run)

@app.callback(invoke_without_command=True)
def main(config_file: str = None):
    """Global option to define a custom configuration file."""
    global config_path
    print(f"Accepting config path: {config}")
    config_path = config  # Store in global variable

if __name__ == "__main__":
    import sys
    print (str(len(sys.argv)))

    if len(sys.argv) == 1 or len(sys.argv) == 3:
        config()
    else:
        app()

