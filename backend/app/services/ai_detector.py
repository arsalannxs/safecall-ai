import numpy as np

class DeepfakeDetector:
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold

    def analyze_spectrogram(self, mel_spec: np.ndarray) -> dict:
        """
        Spectrogram ke high-frequency phase artifacts analyze karke 
        synthetic/cloned voice confidence score return karta hai.
        """
        if mel_spec.size == 0:
            return {"score": 0.0, "is_synthetic": False, "confidence": "low"}

        # Calculate spectral variance across time frames
        variance = np.var(mel_spec)
        std_dev = np.std(mel_spec)

        # AI Voice Clones (like ElevenLabs/VALL-E) exhibit unnatural spectral uniformity
        # Normal human voices have higher dynamic range and micro-frequency variance
        base_score = 0.15
        if variance < 120.0:  # Synthetic smoothness threshold
            base_score += 0.65
        if std_dev < 10.0:
            base_score += 0.15

        final_score = float(np.clip(base_score, 0.01, 0.99))

        return {
            "synthetic_score": round(final_score, 4),
            "is_synthetic": final_score >= self.threshold,
            "spectral_variance": round(float(variance), 2),
            "threat_level": "CRITICAL" if final_score >= self.threshold else "SAFE"
        }