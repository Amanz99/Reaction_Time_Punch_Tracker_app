import sounddevice as sd
import numpy as np
from scipy.signal import find_peaks



def record_audio(fs=44100):
    # Continuously record audio until a punch is detected or timeout
    with sd.InputStream(samplerate=fs, channels=1) as stream:
        for _ in range(5 * fs // 1024):  # Record for up to 5 seconds
            data, _ = stream.read(1024)
            audio_data = np.frombuffer(data, dtype=np.float32)
            if detect_punch(audio_data):
                return audio_data, True
    return None, False


def detect_punch(audio_data, threshold=0.1, fs=44100):
    # Detect a punch in the audio data based on threshold."
    peaks, _ = find_peaks(audio_data, height=threshold)
    return len(peaks) > 0


def get_result():
    # Open the reaction times text file in read mode
    with open('reaction_times.txt', 'r') as file:
        # Read all lines from the file
        lines = file.readlines()

        # Check if there are lines in the file
        if lines:
            # Extract the last line
            last_line = lines[-1].strip()  # Remove any leading/trailing whitespace

            # Print the last line
            print("Last line of results:", last_line)
        else:
            print("No results found in the file.")

