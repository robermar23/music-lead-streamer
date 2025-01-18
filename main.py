import typer
import importlib
from pathlib import Path

app = typer.Typer()

# Path to the "shows" directory, which we load dynamically
SHOWS_PATH = Path(__file__).parent / "show"

@app.command()
def run(
    show: str,
    display: str = typer.Argument(":0", help="Display to run the show on (e.g., ':0')"),
    video_driver: str = typer.Argument("x11", help="Video driver to use (e.g., 'x11')"),
    screen_width: int = typer.Argument(800, help="Screen width (e.g., 800)"),
    screen_height: int = typer.Argument(480, help="Screen height (e.g., 480)"),
    samplerate: int = typer.Argument(44100, help="Sample rate for the audio stream"),
    channels: int = typer.Argument(2, help="Number of audio channels"),
    device_index: int = typer.Argument(None, help="Index of the audio device to use"),
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
    shows = [
        f.stem for f in SHOWS_PATH.glob("*.py")
        # make sure to skip module file
        if f.is_file() and f.stem != "__init__"
    ]
    if not shows:
        typer.echo("No available shows found.")
    else:
        typer.echo("Available shows:")
        for show in shows:
            typer.echo(f"- {show}")
        
if __name__ == "__main__":
    app()
