from .audio import record_audio, listen_for_stop
from .utils import save_all_audio_chunks, save_transcriptions, choose_whisper_model
from .transcribe import Whisper
from .tokenizer import _LANGUAGE_CODE_DICT, _LANGUAGE_CODES, _LANGUAGE_NAMES

import keyboard
import threading
import time

from queue import Queue
from itertools import count
from types import SimpleNamespace

import numpy as np

class RealTime:
    def __init__(self, model_size_or_path="edge", device="auto", start_key: str = 'Enter', stop_key: str = 'Esc', **model_kwargs):
        '''
        Initialize the LiveSTT class.

        Args:
            model_size_or_path: The model size or path "default/edge/model_name" (default is "edge") 
                                Default will choose the best model based on the device configuration
                                Edge will choose the smallest model. Least acc highest performance.
            device: The device to run the model on ("auto", "cpu", or "cuda").
            start_key: str = "Enter",
            stop_key: str = "Esc",
            device_index: int | List[int] = 0,
            compute_type: str = "default",
            cpu_threads: int = 16,
            num_workers: int = 1,
            download_root: str | None = None,
            local_files_only: bool = False,
            files: dict = None,
            **model_kwargs
        
        Help:
            <class>.language_codes: will display the dict of all the languages
        
        '''
        self.start_key = start_key
        self.stop_key = stop_key
        self.available_languages = _LANGUAGE_CODE_DICT
        
        filtered_kwargs = {
                k: v for k, v in model_kwargs.items() if k not in ["model_size_or_path", "device", "start_key", "stop_key"]
            }
        
        # Choose model based on user input or default
        if model_size_or_path == "default":
            # If default, use a preset model name and filter kwargs
            model, device = choose_whisper_model()
            
            self.model_en = Whisper(f"{model}.en", device=device, **filtered_kwargs)
            self.model_multi = Whisper(f"{model}", device=device, **filtered_kwargs)

        elif model_size_or_path == "edge":
            # If a specific model is provided, pass all kwargs
            self.model_en = Whisper("tiny.en", device=device, **filtered_kwargs)
            self.model_multi = Whisper("tiny", device=device, **filtered_kwargs)
            print(f"\nFor '{model_size_or_path}' devices 'tiny', and 'tiny.en' models are loaded")
            
        else:
            # If a specific model is provided, pass all kwargs
            self.model_en = Whisper(f"{model_size_or_path}.en", device=device, **filtered_kwargs)
            self.model_multi = Whisper(f"{model_size_or_path}", device=device, **filtered_kwargs)
            print(f"\n'{model_size_or_path}' and '{model_size_or_path}.en' models are loaded")


    def predict_full(self):
        # Flatten the list of NumPy arrays
        flattened_array = np.concatenate(self.audio_chunks)
        self.audio_id_counter = count()
        if self.task == 'translate':
            self.full_translation = ''
            translate_thread = threading.Thread(target=self.translate_audio, args=(flattened_array,True ))
            translate_thread.start()
        # Transcribe the audio chunk
        print("\nFull Transcribed Recording: \n")
        if self.language == 'en':
            result, _ = self.model_en.transcribe(flattened_array, language=self.language, condition_on_previous_text=False, vad_filter=True)
        else:
            result, _ = self.model_multi.transcribe(flattened_array, language=self.language, condition_on_previous_text=False, vad_filter=True)
        full_transcription = ''
        # Append transcription segments to form complete text
        for segment in result:
            transcription = segment.text
            full_transcription += transcription
            # Filtering Logic to Remove Redundancy
            if transcription.strip():
                for word in transcription.split():
                    print(word, end=' ', flush=True)
                    time.sleep(0.05)
        self.transcriptions['full_transcription'] = full_transcription
        print()
        try:
            translate_thread.join()
            print("\nFull Translated Recording: \n")
            self.maintain_order()
            print()
        except:
            pass

        
    def transcribe_audio(self, audio):
        try:
            # Transcribe the audio chunk
            if self.language == 'en':
                result, _ = self.model_en.transcribe(audio, language=self.language, condition_on_previous_text=False, vad_filter=True)
            else:
                result, _ = self.model_multi.transcribe(audio, language=self.language, condition_on_previous_text=False, vad_filter=True)

            transcription = ''
            # Append transcription segments to form complete text
            for segment in result:
                transcription += segment.text

            # Filtering Logic to Remove Redundancy
            if transcription.strip():
                # Store the transcription with its chunk_id for correct ordering
                chunk_id = next(self.audio_id_counter)
                self.word_queue.put((chunk_id, transcription))
    
        except Exception as e:
            # Queue is empty; continue the loop and wait for new chunks
            print(f"Error during transcription: {e}")


    def translate_audio(self, audio, save=False ):
        try:
            # Transcribe the audio chunk or file 
            result, _ = self.model_multi.transcribe(audio, language=self.language, task=self.task, best_of=10, condition_on_previous_text= True, vad_filter = True)

            transcription = ''
            # Append transcription segments to form complete text
            for segment in result:
                transcription += segment.text

            if save:
                self.transcriptions['full_translation'] = transcription 

            # Filtering Logic to Remove Redundancy
            if transcription.strip():
                # Store the transcription with its chunk_id for correct ordering
                chunk_id = next(self.audio_id_counter)
                self.word_queue.put((chunk_id, transcription))
           
        except Exception as e:
            print(f"Error during translation: {e}")


    def print_words(self, order=0, audio_ids=[], transcriptions=[]):
        id, transcription = self.word_queue.get(timeout=0.1)
        audio_ids.append(id)
        transcriptions.append(transcription)
        audio_ids, transcriptions = map(list, zip(*sorted(zip(audio_ids, transcriptions))))
        if order in audio_ids:
            index = audio_ids.index(order)
            transcription = transcriptions[index]
            self.transcriptions['final_array'].append(transcription)
            for word in transcription.split():
                print(word, end=' ', flush=True)
                time.sleep(0.05)
            audio_ids = audio_ids[index:] 
            transcriptions = transcriptions[index:]
            order += 1
        return order, audio_ids, transcriptions
        

    def maintain_order(self):
        order = 0
        audio_ids = []
        transcriptions = []
        while not self.stop_recording_flag.is_set():
            try:
                order, audio_ids, transcriptions = self.print_words(order, audio_ids, transcriptions)
            except:
                continue
        else:
            while not self.word_queue.empty():
                try:
                    order, audio_ids, transcriptions = self.print_words(order, audio_ids, transcriptions)
                except Exception as e:
                    print(e)
                    continue

    def detect_language(self, threshold):
        print('\nDetecting language..')
        while self.lang_prob < threshold and not self.stop_recording_flag.is_set():
            audio_chunk = record_audio(self.stop_recording_flag, None, duration=3)
            self.language, self.lang_prob, _ = self.model_multi.detect_language(audio_chunk)
        print(f'\nDetected language: {self.language}, ({_LANGUAGE_CODE_DICT[self.language]}) with {self.lang_prob} probability')


    # Transcribe function
    def transcribe(self, 
                   task:str = 'transcribe', 
                   language:str = 'en', 
                   save_recording: bool = False, 
                   save_transcription: bool = False, 
                   save_location: str = None,
                   recording_name: str = None,
                   transcription_name: str = None,
                   full_prediction: bool = False,
                   chunk_size: int = 32000,
                   language_detection_threshold = 0.85,
                   num_threads: int = 4,
                   return_output: bool = False
                   ):
        """
        Transcribes or translates spoken audio based on the specified task and language.

        Parameters:
        - task (str): 
            - 'transcribe': Transcribes spoken audio.
                - If `language` is set to 'english', only English spoken words will be transcribed.
                - If `language` is set to 'auto', it will handle multilingual transcription automatically.
            - 'translate': Translates spoken audio from any language to English.
        - language (str): lanugage code or "Auto". Default is 'auto'.
            - Specifies the target spoken language for the task. Default is 'english'.
            - Please put in the spoken language during translation for better accuracy. 
            - Call <class_object>.available_languages to check available language codes and thier names. 
        - save_recording (bool): Whether to save the audio recording. Default is False.
            - Output format will be in wav file
        - save_transcription (bool): Whether to save the transcription output. Default is False.
            - Output format will be in json file
        - save_location (str): Directory path where the recording and transcription will be saved, if enabled.
        - recording_name (str): Custom name for the saved audio recording file if saving. Default is 'recorded_audio'
        - transcription_name (str): Custom name for the saved transcription file if saving. Default is 'transcriptions'
        - full_prediction (bool): Whether to output prediction on entire audio at the end.
        - chunk_size(int): Amount of audio chunks being passed in 1 second for transcription, Increase for better accurarcy with larger latency
        - language_detection_threshold(int): Keep detecting language until this threashold is reached
        - num_threads(int): Number of parallel threads performing the task. Minimum should be 2
        - return_output(bool): Whether to return the outputs produced as per the parameters

        Returns:
        - return_output(bool): False -> None. Prints the transcription or translations along with other parameter dependent outputs.
        - return_output(bool): True  -> SimpleNameSpace containging:
                                        - audio: a numpy array containing the recorded audio in float32 dtype
                                        - transcriptions: a dictionary containing 
                                            - transcriptions["final_array"]: an array of all the output sentences based on the task
                                        - if full_prediction is set to True
                                            - transcriptions["full_transcription"]: a string containing transciption of full recording      
                                        - if full_prediction is set to True and task is translate
                                            - transcriptions["full_translation"]: a string containing translation of full recording 
                                                                                

        Notes:
        - Ensure the audio input and desired task settings align with the expected functionality for best results.
        """
        
        print(f"\nPress {self.start_key} to start recording or {self.stop_key} to exit.")

        language = language.lower()
        task = task.lower()

        assert task == 'transcribe' or task == 'translate', "Task should be transcribe or translate"
        assert language in list(_LANGUAGE_CODES)+_LANGUAGE_NAMES+['auto'], f'\nLanguage should be one of the following key or value from this dict. \n\n{self.language_codes}'

        if num_threads < 2:
            print("\nWARNING: Num threads should be more than 1, setting to 2")
            num_threads = 2

        if task == 'translate':
            print('\nThe live translate is still in beta. Only English translation is available from other languages.')
    
        self.task = task
        self.word_queue = Queue()
        self.audio_id_counter = count()
        self.stop_recording_flag = None
        self.audio_chunks = []
        self.transcriptions = {'final_array':[]}

        self.language = language if language in _LANGUAGE_CODES else _LANGUAGE_NAMES[_LANGUAGE_CODES.index(language)] if language in _LANGUAGE_NAMES else None if language == 'auto' else None
        self.lang_prob = 1 if self.language else 0
        self.stop_recording_flag = threading.Event()

        while True:
            # Start recording when 'self.start_key' is pressed
            if keyboard.is_pressed(self.start_key):
                print(f"\nRecording... Press {self.stop_key} to stop.")
                self.stop_recording_flag.clear()
                
                # Start the key listening thread 
                stop_listener_thread = threading.Thread(target=listen_for_stop, args=(self.stop_recording_flag, self.stop_key, ))
                stop_listener_thread.start()
                
                self.detect_language(language_detection_threshold) if not self.language else None
                chunk_size = 48000 if self.task == 'translate' and self.language != 'en' else chunk_size

                print_thread = threading.Thread(target=self.maintain_order)
                print_thread.start()
                
                if task == 'transcribe':
                    print("\nTranscribed Text: \n\n", end='', flush=True)
                    # Start recording and transcription
                    self.audio_chunks = record_audio(self.stop_recording_flag, self.transcribe_audio, full_prediction or save_recording, chunk_size=chunk_size, num_threads=num_threads)
                    print_thread.join()
                    print("\nFinal Transcriptions Array: ", self.transcriptions['final_array'])
                    
                else:
                    print("\nTranslated Text: \n\n", end='', flush=True)
                    # Start recording and transcription
                    self.audio_chunks = record_audio(self.stop_recording_flag, self.translate_audio, full_prediction or save_recording, chunk_size=chunk_size, num_threads=num_threads)
                    print_thread.join()
                    print("\nFinal Translations Array: ", self.transcriptions['final_array']) 

                # --------------------------------------------------------------------------------
                # After printing the transcriptions, save audio and transcription files
 
                self.predict_full() if full_prediction else None # Prediction on full recording
                save_all_audio_chunks(self.audio_chunks, save_location, recording_name) if save_recording else None # Save the audio
                save_transcriptions(self.transcriptions, save_location, transcription_name) if save_transcription else None # Save the transcriptions
                
                if return_output:
                    data = {"audio": np.concatenate(self.audio_chunks), 
                            "transcriptions": self.transcriptions}
                    output = SimpleNamespace(**data)
                    return output
                # --------------------------------------------------------------------------------
                break

            # Start recording when 'self.stop_key' is pressed
            elif keyboard.is_pressed(self.stop_key):
                self.stop_recording_flag.set()
                # --------------------------------------------------------------------------------
                break