"""
UNIVERSAL PROCEDURAL AUDIO & ENVELOPE ENGINE
"""
import math
import os
import wave
import numpy as np
import ffmpeg

class ProceduralAudioEngine:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def generate_deterministic_variance(self, base_wav_path: str, seed_index: int, output_wav_path: str) -> str:
        if not os.path.exists(base_wav_path):
            raise FileNotFoundError(f"Missing base WAV: {base_wav_path}")

        shift_percentage = math.sin(seed_index * 137.5) * 0.035
        pitch_factor = 1.0 + shift_percentage
        decay_adjustment = 1.0 + (math.cos(seed_index * 93.1) * 0.10)

        stream = ffmpeg.input(base_wav_path)
        stream = stream.filter('silenceremove', start_periods=1, start_threshold='-50dB')
        stream = stream.filter('asetrate', self.sample_rate * pitch_factor)
        stream = stream.filter('atempo', 1.0 / pitch_factor)
        stream = stream.filter('afade', type='out', start_time=0.8*decay_adjustment, duration=0.2*decay_adjustment)

        ffmpeg.output(stream, output_wav_path, acodec='pcm_s16le', ar=self.sample_rate).overwrite_output().run(quiet=True)
        return output_wav_path

    def generate_dynamic_swell(self, duration_frames: int, fps: int, velocity_array: list, output_wav_path: str) -> str:
        duration_sec = duration_frames / fps
        total_samples = int(duration_sec * self.sample_rate)
        samples_per_frame = int(self.sample_rate / fps)
        
        noise_array = np.random.normal(0, 0.5, total_samples)
        envelope = np.zeros(total_samples)

        if len(velocity_array) != duration_frames:
            raise ValueError("Velocity array length must exactly match duration_frames.")

        for frame_idx, velocity in enumerate(velocity_array):
            start_sample = frame_idx * samples_per_frame
            end_sample = min((frame_idx + 1) * samples_per_frame, total_samples)
            amplitude = max(0.0, min(1.0, float(velocity)))
            envelope[start_sample:end_sample] = amplitude

        fade_frames = 3
        fade_samples = fade_frames * samples_per_frame
        if total_samples > fade_samples:
            envelope[-fade_samples:] *= np.linspace(1.0, 0.0, fade_samples)

        audio_data_int16 = np.int16(noise_array * envelope * 32767)
        temp_raw = f"{output_wav_path}.raw.wav"
        with wave.open(temp_raw, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data_int16.tobytes())

        stream = ffmpeg.input(temp_raw)
        ffmpeg.output(stream, output_wav_path, acodec='pcm_s16le', ar=self.sample_rate, t=duration_sec).overwrite_output().run(quiet=True)
        os.remove(temp_raw)
        return output_wav_path

if __name__ == "__main__":
    pass
