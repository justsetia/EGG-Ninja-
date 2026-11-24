import numpy as np
import wave

sr = 44100
dur = 0.9
N = int(sr * dur)
t = np.arange(N) / sr


f0 = np.where(
    t < 0.08,
    350 + (t / 0.08) * 750,                   
    np.where(
        t < 0.35,
        1100 + 80 * np.sin(2 * np.pi * 8 * t), 
        1100 - 650 * ((t - 0.35) / 0.55) ** 0.7
    )
)

rng = np.random.default_rng(42)
jitter = np.cumsum(rng.standard_normal(N)) * 0.002
jitter -= jitter.mean()
f0 = f0 * (1 + 0.15 * jitter / (np.std(jitter) + 1e-9) * 0.1)


phase = np.cumsum(2 * np.pi * f0 / sr)

saw = 2 * ((phase / (2 * np.pi)) % 1) - 1
source = np.sign(saw) * np.abs(saw) ** 0.6


def formant(x, F, BW):
    r = np.exp(-np.pi * BW / sr)
    theta = 2 * np.pi * F / sr
    b = [1 - r]
    a = [1, -2 * r * np.cos(theta), r * r]
    y = np.zeros_like(x)
    for i in range(1, len(x)):
        y[i] = b[0]*x[i] - a[1]*y[i-1] - a[2]*y[i-2]
    return y

progress = np.clip(t / 0.25, 0, 1)            
F1 = 500 + 700 * progress                      
F2 = 1500 + 800 * progress                      

out = formant(source, F1.mean(), 90)
out = formant(out, F2.mean(), 120)


noise = rng.standard_normal(N) * 0.25
out = out + noise * np.clip(t / 0.1, 0, 1) * np.clip((0.7 - t) / 0.3, 0, 1)


env = np.clip(t / 0.02, 0, 1)                
env *= np.where(t < 0.4, 1.0, np.clip(1 - ((t - 0.4) / 0.5) ** 1.3, 0, 1))
env *= 1 + 0.12 * np.sin(2 * np.pi * 7 * t)     
out *= env


out = np.tanh(out * 3.0)
out = out / np.max(np.abs(out)) * 0.9


with wave.open("cartoon_scream.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sr)
    f.writeframes((out * 32767).astype("<h").tobytes())

print("✓ cartoon_scream.wav")