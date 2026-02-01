import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import os

class VoiceRecorder:
    def __init__(self, samplerate=44100):
        self.samplerate = samplerate
        self.recording = []
        self.is_recording = False
        self.stream = None

    def start_recording(self):
        self.recording = []
        self.is_recording = True
        self.stream = sd.InputStream(callback=self._callback, samplerate=self.samplerate, channels=1)
        self.stream.start()

    def _callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording.append(indata.copy())

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        if not self.recording:
            return None
        
        audio_data = np.concatenate(self.recording, axis=0)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, self.samplerate, audio_data)
        return temp_file.name

    def delete_temp_file(self, file_path):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)