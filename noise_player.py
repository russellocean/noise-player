import numpy as np
import rumps
import simpleaudio as sa
import soundfile as sf
from numpy.fft import irfft
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from scipy import signal

# Set the parameters for the noise
n_samples = 44100 * 10  # 10 seconds of noise at a sample rate of 44100


def brown_noise(n_samples):
    """Generate brown noise using numpy and scipy."""
    # Use an IIR filter to create brown noise from white noise
    wn = np.random.normal(size=n_samples)
    b = [1.0, -0.98]
    a = 1
    bn = signal.lfilter(b, a, wn)
    bn = bn * 0.1 / np.max(np.abs(bn))  # Normalize to -1.0 - 1.0 range
    return bn


def pink_noise(n_samples):
    """Generate pink noise using numpy and scipy."""
    uneven = n_samples % 2
    X = np.random.randn(n_samples // 2 + uneven)
    S = np.sqrt(np.arange(len(X)) + 1.0)  # +1 to avoid divide by zero
    y = (irfft(X / S)).real
    if uneven:
        y = y[:-1]
    y = y * 0.1 / np.max(np.abs(y))  # Normalize to -1.0 - 1.0 range
    return y


def blue_noise(n_samples):
    """Generate blue noise using numpy and scipy."""
    wn = np.random.normal(size=n_samples)
    x = np.fft.rfft(wn)
    s = np.sqrt(
        np.arange(len(x)) + 1.0
    )  # Create a filter with the frequency response of sqrt(f)
    y = np.fft.irfft(x * s)  # Apply it to the white noise in frequency domain
    y = y * 0.1 / np.max(np.abs(y))  # Normalize to -1.0 - 1.0 range
    return y


def generate_noise(noise_type):
    if noise_type == "White":
        noise_gen = WhiteNoise().to_audio_segment(
            duration=10000  # 10 seconds in milliseconds
        )
        noise_gen -= 10  # Reduce volume by 10 dB
        noise_gen.export(f"{noise_type}_noise.wav", format="wav")
    elif noise_type == "Pink":
        pink_noise_samples = pink_noise(n_samples)
        sf.write(f"{noise_type}_noise.wav", pink_noise_samples, 44100)
    elif noise_type == "Brown":
        brown_noise_samples = brown_noise(n_samples)
        sf.write(f"{noise_type}_noise.wav", brown_noise_samples, 44100)
    elif noise_type == "Blue":
        blue_noise_samples = blue_noise(n_samples)
        sf.write(f"{noise_type}_noise.wav", blue_noise_samples, 44100)


def play_noise(noise_type):
    global play_obj, buffer

    # Generate noise and save it as a WAV file
    generate_noise(noise_type)

    # Load the noise WAV file
    wav_file = AudioSegment.from_wav(f"{noise_type}_noise.wav")

    # Convert the noise to a format compatible with simpleaudio
    samples = wav_file.get_array_of_samples()
    buffer = sa.WaveObject(
        samples, wav_file.channels, wav_file.sample_width, wav_file.frame_rate
    )

    if not play_obj or not play_obj.is_playing():
        play_obj = buffer.play()


def stop_noise():
    global play_obj
    if play_obj and play_obj.is_playing():
        play_obj.stop()


class NoiseApp(rumps.App):
    def __init__(self):
        super(NoiseApp, self).__init__("Noise Player")
        self.menu = [
            "Play",
            "Stop",
            rumps.MenuItem("Noise Type", ["White", "Pink", "Brown", "Blue"]),
        ]
        self.noise_type = "White"

    @rumps.clicked("Play")
    def play(self, _):
        play_noise(self.noise_type)

    @rumps.clicked("Stop")
    def stop(self, _):
        stop_noise()

    @rumps.clicked("Noise Type", "White")
    def set_white(self, _):
        self.noise_type = "White"

    @rumps.clicked("Noise Type", "Pink")
    def set_pink(self, _):
        self.noise_type = "Pink"

    @rumps.clicked("Noise Type", "Brown")
    def set_brown(self, _):
        self.noise_type = "Brown"

    @rumps.clicked("Noise Type", "Blue")
    def set_blue(self, _):
        self.noise_type = "Blue"


play_obj = None
buffer = None

if __name__ == "__main__":
    NoiseApp().run()
