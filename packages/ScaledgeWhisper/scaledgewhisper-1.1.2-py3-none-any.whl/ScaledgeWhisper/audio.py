"""We use the PyAV library to decode the audio: https://github.com/PyAV-Org/PyAV

The advantage of PyAV is that it bundles the FFmpeg libraries so there is no additional
system dependencies. FFmpeg does not need to be installed on the system.

However, the API is quite low-level so we need to manipulate audio frames directly.
"""

import gc
import io
import itertools

from typing import BinaryIO, Union
from concurrent.futures import ThreadPoolExecutor

import av
import numpy as np
import torch
import pyaudio
import time
import keyboard


def decode_audio(
    input_file: Union[str, BinaryIO],
    sampling_rate: int = 16000,
    split_stereo: bool = False,
):
    """Decodes the audio.

    Args:
      input_file: Path to the input file or a file-like object.
      sampling_rate: Resample the audio to this sample rate.
      split_stereo: Return separate left and right channels.

    Returns:
      A float32 Numpy array.

      If `split_stereo` is enabled, the function returns a 2-tuple with the
      separated left and right channels.
    """
    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono" if not split_stereo else "stereo",
        rate=sampling_rate,
    )

    raw_buffer = io.BytesIO()
    dtype = None

    with av.open(input_file, mode="r", metadata_errors="ignore") as container:
        frames = container.decode(audio=0)
        frames = _ignore_invalid_frames(frames)
        frames = _group_frames(frames, 500000)
        frames = _resample_frames(frames, resampler)

        for frame in frames:
            array = frame.to_ndarray()
            dtype = array.dtype
            raw_buffer.write(array)

    # It appears that some objects related to the resampler are not freed
    # unless the garbage collector is manually run.
    # https://github.com/SYSTRAN/faster-whisper/issues/390
    # note that this slows down loading the audio a little bit
    # if that is a concern, please use ffmpeg directly as in here:
    # https://github.com/openai/whisper/blob/25639fc/whisper/audio.py#L25-L62
    del resampler
    gc.collect()

    audio = np.frombuffer(raw_buffer.getbuffer(), dtype=dtype)

    # Convert s16 back to f32.
    audio = audio.astype(np.float32) / 32768.0

    if split_stereo:
        left_channel = audio[0::2]
        right_channel = audio[1::2]
        return torch.from_numpy(left_channel), torch.from_numpy(right_channel)

    return torch.from_numpy(audio)


def _ignore_invalid_frames(frames):
    iterator = iter(frames)

    while True:
        try:
            yield next(iterator)
        except StopIteration:
            break
        except av.error.InvalidDataError:
            continue


def _group_frames(frames, num_samples=None):
    fifo = av.audio.fifo.AudioFifo()

    for frame in frames:
        frame.pts = None  # Ignore timestamp check.
        fifo.write(frame)

        if num_samples is not None and fifo.samples >= num_samples:
            yield fifo.read()

    if fifo.samples > 0:
        yield fifo.read()


def _resample_frames(frames, resampler):
    # Add None to flush the resampler.
    for frame in itertools.chain(frames, [None]):
        yield from resampler.resample(frame)


def pad_or_trim(array, length: int = 3000, *, axis: int = -1):
    """
    Pad or trim the Mel features array to 3000, as expected by the encoder.
    """
    axis = axis % array.ndim
    if array.shape[axis] > length:
        idx = [Ellipsis] * axis + [slice(length)] + [Ellipsis] * (array.ndim - axis - 1)
        return array[idx]

    if array.shape[axis] < length:
        pad_widths = (
            [
                0,
            ]
            * array.ndim
            * 2
        )
        pad_widths[2 * axis] = length - array.shape[axis]
        array = torch.nn.functional.pad(array, tuple(pad_widths[::-1]))

    return array


# Function to record audio
def record_audio(stop_recording_flag, func, keep_all=False, chunk_size=24000, duration: int = None, num_threads = 4):
    transcription_threads = []
    audio_chunks = []
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Audio settings
    rate = 16000  # Sample rate
    chunk_size = chunk_size  # Buffer size for capturing audio
    channels = 1  # Mono
    format = pyaudio.paFloat32  # 32-bit audio
    seconds = duration if duration else 1  # Either 1 second or 
    
    # Open audio stream
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    executor = ThreadPoolExecutor(max_workers=num_threads) if not duration else None # Thread pool for transcription

    # Continue recording until 'x' is pressed
    while not stop_recording_flag.is_set() and not duration:
        frames = []

        # Capture audio for chunks_size length
        for _ in range(seconds):
            data = stream.read(chunk_size, exception_on_overflow=False)
            frames.append(data)
        
        # Convert frames to numpy array
        chunk = np.frombuffer(b''.join(frames), dtype=np.float32)
    
        # Combine the frames into a single audio chunk
        chunk_tensor = torch.tensor(chunk)

        # Append the audio_chunks
        audio_chunks.append(chunk) if keep_all else None

        # Start a thread for transcription to avoid blocking recording
        transcription_thread = executor.submit(func, chunk_tensor, )
        transcription_threads.append(transcription_thread)
    else:
        if duration:
            frames = []

            # Capture audio for chunks_size length
            for _ in range(seconds):
                data = stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            # Convert frames to numpy array
            chunk = np.frombuffer(b''.join(frames), dtype=np.float32)
        
            # Combine the frames into a single audio chunk
            chunk_tensor = torch.tensor(chunk)


    # Stop the audio stream and close PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()
    executor.shutdown(wait=True) if executor else None # Wait for all transcription threads to finish
    print("\n\nRecording stopped.") if stop_recording_flag.is_set() else None
    return audio_chunks if not duration else chunk_tensor


# Function to listen for the 'x' key press to stop the recording
def listen_for_stop(stop_recording_flag, key):
    while True:
        if keyboard.is_pressed(key):
            stop_recording_flag.set()  # Set the stop_recording_flag to stop the recording
            break
        time.sleep(0.1)  # Sleep to avoid CPU overload