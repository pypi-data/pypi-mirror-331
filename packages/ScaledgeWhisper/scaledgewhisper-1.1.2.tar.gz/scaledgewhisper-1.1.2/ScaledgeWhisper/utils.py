import logging
import os
import re

from typing import List, Optional

import huggingface_hub
import requests
import pyaudio
import wave
import json

import torch
import psutil
import GPUtil

from tqdm.auto import tqdm

import numpy as np

_MODELS = {
    "tiny.en": "Systran/faster-whisper-tiny.en",
    "tiny": "Systran/faster-whisper-tiny",
    "base.en": "Systran/faster-whisper-base.en",
    "base": "Systran/faster-whisper-base",
    "small.en": "Systran/faster-whisper-small.en",
    "small": "Systran/faster-whisper-small",
    "medium.en": "Systran/faster-whisper-medium.en",
    "medium": "Systran/faster-whisper-medium",
    "large-v1": "Systran/faster-whisper-large-v1",
    "large-v2": "Systran/faster-whisper-large-v2",
    "large-v3": "Systran/faster-whisper-large-v3",
    "large": "Systran/faster-whisper-large-v3",
    "distil-large-v2": "Systran/faster-distil-whisper-large-v2",
    "distil-medium.en": "Systran/faster-distil-whisper-medium.en",
    "distil-small.en": "Systran/faster-distil-whisper-small.en",
    "distil-large-v3": "Systran/faster-distil-whisper-large-v3",
    "large-v3-turbo": "mobiuslabsgmbh/faster-whisper-large-v3-turbo",
    "turbo": "mobiuslabsgmbh/faster-whisper-large-v3-turbo",
}


def available_models() -> List[str]:
    """Returns the names of available models."""
    return list(_MODELS.keys())


def get_assets_path():
    """Returns the path to the assets directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def get_logger():
    """Returns the module logger."""
    return logging.getLogger("faster_whisper")


def download_model(
    size_or_id: str,
    output_dir: Optional[str] = None,
    local_files_only: bool = False,
    cache_dir: Optional[str] = None,
):
    """Downloads a CTranslate2 Whisper model from the Hugging Face Hub.

    Args:
      size_or_id: Size of the model to download from https://huggingface.co/Systran
        (tiny, tiny.en, base, base.en, small, small.en, distil-small.en, medium, medium.en,
        distil-medium.en, large-v1, large-v2, large-v3, large, distil-large-v2,
        distil-large-v3), or a CTranslate2-converted model ID from the Hugging Face Hub
        (e.g. Systran/faster-whisper-large-v3).
      output_dir: Directory where the model should be saved. If not set, the model is saved in
        the cache directory.
      local_files_only:  If True, avoid downloading the file and return the path to the local
        cached file if it exists.
      cache_dir: Path to the folder where cached files are stored.

    Returns:
      The path to the downloaded model.

    Raises:
      ValueError: if the model size is invalid.
    """
    if re.match(r".*/.*", size_or_id):
        repo_id = size_or_id
    else:
        repo_id = _MODELS.get(size_or_id)
        if repo_id is None:
            raise ValueError(
                "Invalid model size '%s', expected one of: %s"
                % (size_or_id, ", ".join(_MODELS.keys()))
            )

    allow_patterns = [
        "config.json",
        "preprocessor_config.json",
        "model.bin",
        "tokenizer.json",
        "vocabulary.*",
    ]

    kwargs = {
        "local_files_only": local_files_only,
        "allow_patterns": allow_patterns,
        "tqdm_class": disabled_tqdm,
    }

    if output_dir is not None:
        kwargs["local_dir"] = output_dir
        kwargs["local_dir_use_symlinks"] = False

    if cache_dir is not None:
        kwargs["cache_dir"] = cache_dir

    try:
        return huggingface_hub.snapshot_download(repo_id, **kwargs)
    except (
        huggingface_hub.utils.HfHubHTTPError,
        requests.exceptions.ConnectionError,
    ) as exception:
        logger = get_logger()
        logger.warning(
            "An error occured while synchronizing the model %s from the Hugging Face Hub:\n%s",
            repo_id,
            exception,
        )
        logger.warning(
            "Trying to load the model directly from the local cache, if it exists."
        )

        kwargs["local_files_only"] = True
        return huggingface_hub.snapshot_download(repo_id, **kwargs)


def format_timestamp(
    seconds: float,
    always_include_hours: bool = False,
    decimal_marker: str = ".",
) -> str:
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
    )


class disabled_tqdm(tqdm):
    def __init__(self, *args, **kwargs):
        kwargs["disable"] = True
        super().__init__(*args, **kwargs)


def get_end(segments: List[dict]) -> Optional[float]:
    return next(
        (w["end"] for s in reversed(segments) for w in reversed(s["words"])),
        segments[-1]["end"] if segments else None,
    )

# Function to assess system resources
def get_system_resources():
    cpu_cores = psutil.cpu_count(logical=False)  # Number of physical CPU cores
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total  # Total system memory in bytes
    available_memory = memory_info.available  # Available memory in bytes
    gpu_count = len(GPUtil.getGPUs())  # Check if GPU is available

    # If system has GPU, we can opt for larger models
    has_gpu = gpu_count > 0

    # Return system resources as a dictionary
    return {
        "cpu_cores": cpu_cores,
        "total_memory": total_memory,
        "available_memory": available_memory,
        "has_gpu": has_gpu,
    }

# Function to automatically choose Whisper model
def choose_whisper_model():
    resources = get_system_resources()

    # Extract system resource details
    cpu_cores = resources["cpu_cores"]
    total_memory = resources["total_memory"]
    available_memory = resources["available_memory"]
    has_gpu = resources["has_gpu"]

    # Determine the model based on system resources
    if has_gpu:
        # If GPU is available, we can go for a larger model
        if total_memory >= 16 * 1024**3:  # 16 GB or more
            model = "large"
        elif total_memory >= 8 * 1024**3:  # 8 GB or more
            model = "medium"
        else:
            model = "small"
    else:
        # If no GPU, rely on CPU and available memory
        if cpu_cores >= 8 and available_memory >= 8 * 1024**3:  # 8 GB or more memory
            model = "base"
        else:
            model = "tiny"
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Chosen {model} and {model}.en model with {device} device\n")
    return model, device

# Function to save all recorded audio chunks into a single file
def save_all_audio_chunks(audio_chunks: list, saved_data_folder: str = None, file_name: str = None):
    if not saved_data_folder:
        saved_data_folder = 'saved_data'
    if not os.path.exists(saved_data_folder):
        os.makedirs(saved_data_folder, exist_ok=True)

    # Check if the file already exists and append a number to the filename if necessary
    if not file_name:
        file_name = "recorded_audio"
    base, _ = os.path.splitext(file_name)
    if os.path.exists(os.path.join(saved_data_folder, f"{base}.wav")):
        print('\nFile already exits ',os.path.join(saved_data_folder, f"{base}.wav"),"\nSaving as ", end="")
        i = 1
        # Keep adding a number to the filename until we find a unique one
        while os.path.exists(os.path.join(saved_data_folder, f"{base}_{i}.wav")):
            i += 1
        # Set the new filepath with the number added
        audio_file_path = os.path.join(saved_data_folder, f"{base}_{i}.wav")
        print(audio_file_path)
    else:
        # Use the filepath directly if it does not exist
        audio_file_path = os.path.join(saved_data_folder, f"{base}.wav")

    p = pyaudio.PyAudio()
    rate = 16000
    channels = 1
    format = pyaudio.paInt16

    # Write all chunks into a single audio file
    with wave.open(audio_file_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        for chunk in audio_chunks:
            int_chunk = (chunk * 32767).astype(np.int16)
            chunk = int_chunk.tobytes()
            wf.writeframes(chunk)
    
    print(f"\nFull recording saved to {os.path.join(os.path.dirname(os.path.abspath(audio_file_path)), os.path.basename(audio_file_path))}")


# Function to save the transcriptions array to a file in the 'saved_data' folder
def save_transcriptions(transcriptions: list, saved_data_folder: str = None, file_name: str = None):
    if not saved_data_folder:
        saved_data_folder = 'saved_data'
    if not os.path.exists(saved_data_folder):
        os.makedirs(saved_data_folder, exist_ok=True)

    # Check if the file already exists and append a number to the filename if necessary
    if not file_name:
        file_name = "transcriptions"
    base, extension = os.path.splitext(file_name)
    if os.path.exists(os.path.join(saved_data_folder, f"{base}.json")):
        print('\nFile already exits ',os.path.join(saved_data_folder, f"{base}.json"),"\nSaving as ", end="")
        i = 1
        # Keep adding a number to the filename until we find a unique one
        while os.path.exists(os.path.join(saved_data_folder, f"{base}_{i}.json")):
            i += 1
        # Set the new filepath with the number added
        transcription_file_path = os.path.join(saved_data_folder, f"{base}_{i}.json")
        print(transcription_file_path)
    else:
        # Use the filepath directly if it does not exist
        transcription_file_path = os.path.join(saved_data_folder, f"{base}.json")

    # Save the transcriptions list as a JSON file
    with open(transcription_file_path, 'w') as f:
        json.dump(transcriptions, f, indent=4)

    print(f"\nTranscriptions saved to {os.path.join(os.path.dirname(os.path.abspath(transcription_file_path)), os.path.basename(transcription_file_path))}")