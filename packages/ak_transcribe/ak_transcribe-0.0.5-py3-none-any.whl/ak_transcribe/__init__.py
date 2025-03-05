"Transcribe Media Files"
__version__ = "0.0.5"

from rich.console import Console
from rich.panel import Panel

from ak_transcribe import converter
from ak_transcribe.transcriber import Transcriber, TranscribedContent

from rich.console import Console

console = Console()


def test_configs():
    """Tests if the config_file is correctly set up"""
    from ak_transcribe.utils.config_parser import Config

    _config = Config()
    console = Console()

    module_name = __name__
    console.print(f"[bold magenta]Module: {module_name}[/bold magenta]\n")

    def _config_vals_ok(keys: tuple[str, ...], default="NAN") -> bool:
        return _config.get(keys=keys, default=default) != default

    # Define a helper to format the output
    def check_configs(title, vals_to_check):
        with console.status(f"[bold cyan]Checking {title} configs...", spinner="dots"):
            if all([_config_vals_ok(x) for x in vals_to_check]):
                console.print(
                    Panel(f"[green bold]OK", title=title, border_style="green")
                )
            else:
                console.print(
                    Panel(f"[red bold]Not OK", title=title, border_style="red")
                )

    # FFMPEG check
    check_configs("ffmpeg", [("ffmpeg", "cmd"), ("ffmpeg", "transcode_dir")])

    # Whisper-Docker check
    check_configs("Whisper-Docker", [("whisper", "url")])

    # Whisper-CPU check
    check_configs("Wisper-CPU", [("whisper", "model"), ("whisper", "device")])
