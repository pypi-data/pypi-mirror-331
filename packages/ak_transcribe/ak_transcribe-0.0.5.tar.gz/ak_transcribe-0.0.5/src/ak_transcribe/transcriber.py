import json
import shutil

import warnings
from functools import lru_cache
from pathlib import Path

import requests
from groq import Groq
from ak_transcribe.filehandler import TempMp3, check_filemime, run_command

from ak_transcribe.utils.config_parser import Config
from ak_transcribe.console import console

_config = Config()


class TranscribedContent:
    def __init__(self, results: dict | Path) -> None:
        assert results is not None
        if isinstance(results, Path):
            assert results.suffix.casefold().endswith(".json")
            assert results.exists()
            with open(results, "r", encoding="utf-8") as f:
                self._results = json.load(f)
        elif isinstance(results, dict):
            self._results = results
        else:
            raise Exception(f"Expected type: dict|JSONfilepath, got {type(results)}")

    @property
    def txt(self) -> str:
        assert isinstance(self._results, dict), "Results not set yet"
        return "\n".join(
            [line["text"].strip() for line in self._results["segments"]]  # type: ignore
        )

    @property
    def srt(self) -> str:
        assert isinstance(self._results, dict), "Results not set yet"
        count = 0
        text_blob = ""
        for segment in self._results.get("segments", []):
            count += 1
            _timestamp_start: str = f"{count}\n{self.__srt_time(segment['start'])}"
            _timestamp_end: str = f"{self.__srt_time(segment['end'])}\n"
            _text: str = f"{segment['text'].replace('-->', '->').strip()}"
            text_blob += f"{_timestamp_start} --> {_timestamp_end}{_text}\n\n"
        return text_blob

    @property
    def json(self) -> str:
        """Return str representation of json object"""
        assert isinstance(self._results, dict), "Results not set yet"
        return json.dumps(self._results, indent=4)

    @staticmethod
    def __srt_time(_seconds: float) -> str:
        """Convert seconds into SRT (SubRip Text) time format."""
        assert _seconds >= 0, "non-negative timestamp expected"
        milliseconds: int = round(_seconds * 1000.0)
        hours: int = milliseconds // 3_600_000
        milliseconds -= hours * 3_600_000
        minutes: int = milliseconds // 60_000
        milliseconds -= minutes * 60_000
        seconds: int = milliseconds // 1_000
        milliseconds -= seconds * 1_000
        return (f"{hours}:") + f"{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def embed_srt(self, filepath: Path):
        if not check_filemime(filepath=filepath, mime_str="video"):
            console.print(f"[bold red] File ({filepath.name} is not a video file.)")
            return

        # Make sure the ".srt" file is setup
        temp_srt = filepath.with_suffix(".srt")
        if not temp_srt.is_file():
            with open(temp_srt, "w", encoding="utf-8") as f:
                f.write(self.srt)

        # Path definitions
        __ffmpeg_path: Path | str = Path(
            _config.get(keys=("ffmpeg", "cmd"), default="ffmpeg")
        )
        _tempoutput: Path = Path(".") / f"{filepath.stem}-Temp{filepath.suffix}"

        # FFmpeg command setup
        command = [
            f'"{__ffmpeg_path}"',
            "-loglevel quiet",
            "-stats -hide_banner",
            f'-i "{filepath}"',
            f'-i "{temp_srt}"',
            "-c:v copy",
            "-c:a copy",
            "-c:s mov_text",
            f'"{_tempoutput}"',
            "-y",
        ]
        command = " ".join(command)
        console.print(f"[green]FFmpeg cmd: [/green][grey]{command}[/grey]")
        # Run the process
        with console.status(f"Embedding subtitles into {filepath.name}..."):
            if run_command(command=command) != 0:
                raise Exception("Embedding subtitles failed.")
            shutil.move(_tempoutput, filepath)
            temp_srt.unlink()

        console.print(f"[green]Embedding Successful![/green]")


class OpenAI_CPU:
    def __init__(self) -> None:
        try:
            import whisper  # type: ignore
        except ModuleNotFoundError:
            raise Exception(
                (
                    "Whisper not installed. "
                    "Install using `pip install -r pyproject.toml --extra cpu`"
                )
            )

        model = _config.get(keys=("whisper", "model"), default="small.en")
        device = _config.get(keys=("whisper", "device"), default="cpu")
        self.__whisper = whisper.load_model(model, device=device)

    def process(self, filepath: Path) -> TranscribedContent:
        """Process the file and save results to `self._results`"""
        with TempMp3(filepath=filepath) as file:
            with warnings.catch_warnings(action="ignore"):
                console.print(f"[yellow]Processing file:[/yellow] {file}")
                results = self.__whisper.transcribe(str(file))
                console.print(f"[green]Processing complete![/green]")
                return TranscribedContent(results=results)


class OpenAI_webserver:
    def __init__(self) -> None:

        self.__base_url: str = _config.get(keys=("whisper", "url"), default="")
        assert self.__base_url != "", "Make sure [whisper][url] is set in `config.toml`"
        requests.get(self.__base_url).raise_for_status()

        self.__transcript_url = f"{self.__base_url.rstrip('/')}/asr?encode=true&task=transcribe&word_timestamps=true&output=json"
        console.print(f"[green]Using Whisper webserver")

    def process(self, filepath: Path) -> TranscribedContent:
        """Process the file and save results to `self._results`"""
        json_path = filepath.with_suffix(".json")
        if json_path.is_file():
            console.print(f"[green]Existing Transcription Found![/green]")
            with open(json_path, "r", encoding="utf-8") as f:
                return TranscribedContent(results=json.load(f))

        with TempMp3(filepath=filepath) as file:
            audio_file_path = str(file)
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()
            _files = {
                "audio_file": (
                    audio_file_path,
                    audio_data,
                    "audio/mpeg",
                )
            }
            with console.status("Sending request to server...") as status:
                response = requests.post(self.__transcript_url, files=_files)
                response.raise_for_status()
                console.print(f"[green]Received transcription successfully![/green]")
                return TranscribedContent(results=response.json())


class GroqTranscriber:
    def __init__(self):
        self.__client = Groq(api_key=_config.get(keys=("groq", "key"), default=""))
    
    def process(self, filepath: Path) -> TranscribedContent:
        
        with TempMp3(filepath=filepath) as file:
            with open(str(file), "rb") as f:
                with console.status("Sending request to server...") as status:
                    
                    transcription = self.__client.audio.transcriptions.create(
                    file=(filepath.name, f.read()),
                    model="distil-whisper-large-v3-en",
                    response_format="verbose_json",
                    )
                    console.print(f"[green]Received transcription successfully![/green]")
                return TranscribedContent(json.loads(transcription.model_dump_json()))


@lru_cache(maxsize=1)
def _get_processor() -> OpenAI_webserver | OpenAI_CPU:
    if _config.get(keys=("groq", "key"), default="") != "":
        return GroqTranscriber()
    try:
        return OpenAI_webserver()
    except Exception as e:
        console.print(f"[red]Web server processor failed:[/red] {e}")
        console.print("[yellow]Attempting CPU Processing...[/yellow]")
        return OpenAI_CPU()


Transcriber: OpenAI_webserver | OpenAI_CPU |GroqTranscriber = _get_processor()
