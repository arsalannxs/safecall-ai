import io
import numpy as np
import librosa

class AudioProcessor:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def bytes_to_audio_array(self, raw_bytes: bytes) -> np.ndarray:
        """Raw audio bytes ko float32 numpy array mein convert karta hai."""
        try:
            # 16-bit PCM buffer conversion
            audio_data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
            # Normalize signal between -1.0 and 1.0
            audio_data /= 32768.0
            return audio_data
        except Exception as e:
            print(f"[AUDIO ERROR] Conversion failed: {e}")
            return np.array([], dtype=np.float32)

    def extract_mel_spectrogram(self, audio_array: np.ndarray) -> np.ndarray:
        """Audio array se Mel-Spectrogram feature matrix generate karta hai."""
        if len(audio_array) == 0:
            return np.array([])
        
        # Extract Mel Spectrogram features using librosa
        spectrogram = librosa.feature.melspectrogram(
            y=audio_array,
            sr=self.sample_rate,
            n_mels=128,
            fmax=8000
        )
        # Convert power spectrogram to decibel units
        db_spectrogram = librosa.power_to_db(spectrogram, ref=np.max)
        return db_spectrogram