from .live_transcribe import RealTime
from .utils import _MODELS
from .transcribe import Whisper
from .utils import choose_whisper_model
from .tokenizer import _LANGUAGE_CODE_DICT, _LANGUAGE_CODES, _LANGUAGE_NAMES

import os
import argparse
import torch
import warnings
import time
from queue import Queue
import threading

# Suppress all warnings
warnings.filterwarnings("ignore")


def transcribe_audio(stt, file_path, args, word_queue, stop_flag):
        print()
        print('\n', "X --- X --- X --- X",'\n')
        # Extract file name without extension
        file_name = os.path.basename(file_path)  # Get the file name including extension
        print("File Name: \n")
        print(os.path.splitext(file_name)[0], '\n')  # Remove extension

        multilingual = True if args.language and args.language == 'multi' else False
        args.language = None if multilingual else args.language

        result, info = stt.transcribe(file_path, task=args.task[0], language=args.language, multilingual=multilingual, output_language='hybrid', vad_filter=True)
        
        # Put the info into the queue (this will be handled by the print_info function)
        if args.info and info:
            print_info(info) # Print info if info

        print("Transcription: \n") if args.task[0] == 'transcribe' else print("Translation: \n")

        for segment in result:
            transcription = segment.text.strip()
            if transcription:
                for word in transcription.split():
                    word_queue.put(word)  # Add words to the queue
        stop_flag.set()  # Signal transcription completion



def print_info(info):
    print('Info: ')
    print(f'Language     = {info.language}')
    print(f'Lang Prob    = {info.language_probability:.3f}')
    print(f'Duration     = {info.duration:.2f}')
    print(f'VAD Duration = {info.duration_after_vad:.2f}\n')



def print_words(file_path, args, word_queue, stop_flag):
    while not stop_flag.is_set() or not word_queue.empty():
        try:
            word = word_queue.get(timeout=0.1)  # Get the next word from the queue
            print(word, end=' ', flush=True)
            time.sleep(0.05)  # Delay to simulate real-time printing
        except:
            continue  # Wait if the queue is temporari5ly empty
    print()



def handle_task(args):
    if args.live:
        if args.paths:
            return print("Cannot specify both --live and audio paths. Choose one.")
        rstt = RealTime(args.model)
        rstt.transcribe(args.task[0], 
                            args.live_language,
                            args.save_recording,
                            args.save_transcription,
                            args.save_location,
                            args.recording_name,
                            args.transcription_name,
                            args.full_prediction,
                            args.chunk_size,
                            num_threads=args.num_threads,
                            )
        
    else:
        args.paths = args.task[1:] if len(args.task) > 1 else None
        if not args.paths:
            return print('An audio path is required for non-live tasks.')
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if args.model == 'default':
            model, device = choose_whisper_model()
        elif args.model == 'edge':
            model = 'tiny'
        else:
            model = args.model
        if args.language == 'en':
            if model.endswith('.en'):
                stt = Whisper(model, device)
            else:
                try:
                    stt = Whisper(model+'.en', device)           
                except Exception as e:
                    raise e
        else:
            try: 
                stt = Whisper(model, device)
            except Exception as e:
                raise
        for file_path in args.paths:
            # Append transcription segments to form complete text
            word_queue = Queue()  # Queue to hold words for printing
            stop_flag = threading.Event()  # Event to signal transcription completion
            # Start transcription and printing threads
            transcription_thread = threading.Thread(target=transcribe_audio, args=(stt, file_path, args, word_queue, stop_flag, ))
            transcription_thread.start()
            print_words(file_path, args, word_queue, stop_flag)

            # Wait for both threads to finish
            transcription_thread.join()
        print("\n", "X --- X --- X --- X")


def handle_args(args):
    value = None 
    if args.list_models:
        [print(i) for i in list(_MODELS.keys())]
        print()
        value = 1
    
    if args.available_languages:
        print('For live: \nDefault - auto')
        print('\nFor non live: \nDefault - multi')
        print('\nCommon in both: ')
        [print(i,":",j) for i,j in _LANGUAGE_CODE_DICT.items()]
        print()
        value = 1

    if args.task[0] not in ['translate','transcribe'] and not args.paths and args.info:
        args.paths = args.task
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        stt = Whisper('tiny', device)
        for file_path in args.paths:
            print('\n', "X --- X --- X --- X",'\n')
            # Extract file name without extension
            file_name = os.path.basename(file_path)  # Get the file name including extension
            print("File Name: \n")
            print(os.path.splitext(file_name)[0], '\n')  # Remove extension
            try:
                _, info = stt.transcribe(file_path,  vad_filter=True)
                # Put the info into the queue (this will be handled by the print_info function)
                if args.info and info:
                    print_info(info) # Print info if info
            except Exception as e:
                print(e)
        print('\n', "X --- X --- X --- X")
        value = 1

    if args.task[0] in ['translate','transcribe']:
        handle_task(args)
        value = 1

    return value 


def main():
    parser = argparse.ArgumentParser(description="A command-line tool for ScaledgeWhisper.",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('task', nargs='*',default=[0], help="Choose task to perform, Choose between 'transcribe' or 'translate'")
    parser.add_argument('paths', nargs='*', help='Provide audio paths in non-live task')
    parser.add_argument('--list_models', action='store_true', help='List all the available whisper models')
    parser.add_argument('--available_languages', action='store_true', help='List all the available languages for live and non-live task')
    parser.add_argument('--info', action='store_true',help='Provide info on audio paths such as language, language probability, duration')
    parser.add_argument('--live', action='store_true', help='Whether to do live transcription or translation')
    parser.add_argument('--live_language', default='auto', choices=list(_LANGUAGE_CODES)+_LANGUAGE_NAMES+['auto'], help='Specify the language for live task. Default is Auto')
    parser.add_argument('--language', default=None, choices=list(_LANGUAGE_CODES)+_LANGUAGE_NAMES+['multi'], help='Specify the language of detection for non live task. Default is autodetect')
    parser.add_argument('--model', default='default', help='Intended platform. edge, default, model name or path. Default is default, model will be selected according to platform config')
    parser.add_argument('--save_recording', action='store_true', help='Whether to save the recording after live task')
    parser.add_argument('--save_transcription', action='store_true', help='Whether to save the transcription after live task')
    parser.add_argument('--save_location', default=None, help='Where to save the files after live task default will be the cwd')
    parser.add_argument('--recording_name', default=None, help='Name of the recorded file after live task default full_recording.wab')
    parser.add_argument('--transcription_name', default=None, help='Name of the transcripted file after live task default will be the transcriptions.json')
    parser.add_argument('--full_prediction', action='store_true', help='Whether to do perform the transciption and translation depending upon the task on the full recording')
    parser.add_argument('--chunk_size', default=32000, type=int, help='Size of audio chunk per second to send for performing the task. The larger the better accuracy but with higher latency')
    parser.add_argument('--num_threads', default=4, type=int, help='Num of threads to perform parallelism. Minimum should be 2')
    args = parser.parse_args()
    
    print()
    parser.print_help() if not handle_args(args) else None

    


