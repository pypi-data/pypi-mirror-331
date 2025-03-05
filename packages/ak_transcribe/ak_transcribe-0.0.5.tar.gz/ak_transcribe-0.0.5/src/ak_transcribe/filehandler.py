from pathlib import Path
from ak_transcribe.utils.config_parser import Config
from functools import lru_cache
from ak_transcribe.console import console
import subprocess
from typing import Literal

_config = Config()


class TempMp3:
    def __init__(self, filepath: Path):
        self.__ffmpeg_path: Path | str = Path(
            _config.get(keys=("ffmpeg", "cmd"), default="ffmpeg")
        )
        self.filepath = filepath
        assert self.filepath.exists()
        self.__unique_mp3file: bool = not self.is_audio(filepath=filepath)

    @lru_cache(maxsize=1)
    def __mp3_path(self) -> Path:
        if self.__unique_mp3file:
            return self.__convert_to_audio(file=self.filepath)
        else:
            return self.filepath

    def __enter__(self) -> Path:
        return self.__mp3_path()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            console.print(f"[red]An exception occurred:[/red] {exc_type} - {exc_value}")
        if not self.is_audio(filepath=self.filepath):
            self.__mp3_path().unlink()
        return False

    def __convert_to_audio(self, file: Path) -> Path:
        """Convert the given audio file to an m4a format."""
        outputpath = (
            Path(_config.get(keys=("ffmpeg", "transcode_dir"), default="."))
            / f"{file.stem}_temp.m4a"
        )
        # ffmpeg -i input.mp4 -ac 1 -ar 16000 -b:a 24k -c:a aac output.m4a
        command = f'"{self.__ffmpeg_path}" -loglevel quiet -stats -hide_banner -i "{file}" -ac 1 -ar 16000 -b:a 24K -c:a aac "{outputpath}" -y'
        with console.status("Converting to m4a...") as status:
            if run_command(command=command) != 0:
                raise Exception("Conversion to `.m4a` failed.")
        console.print(
            f"[green]Conversion successful![/green] Output saved to: {outputpath}"
        )
        return outputpath

    def is_video(self) -> bool:
        """Check if the given file is video"""
        return check_filemime(filepath=self.filepath, mime_str="video")

    @staticmethod
    def is_audio(filepath: Path) -> bool:
        """Check if the given file is audio"""
        return False        # Force Transcription
        return check_filemime(filepath=filepath, mime_str="audio")


def check_filemime(filepath: Path, mime_str: Literal["video", "audio"]):
    ext = filepath.suffix.casefold().strip()
    match mime_str.strip().casefold():
        case "video":
            _ext = (".mp4", ".mkv")
            return ext in _ext

        case "audio":
            _ext = (".mp3",".m4a")
            return ext in _ext
        case _:
            raise Exception(f"Invalid mimetype: {mime_str}")


def run_command(command: str) -> int:
    """Run shell commands using Subprocess; Returns the process returncode"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.returncode
