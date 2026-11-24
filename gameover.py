import wave
import struct
import math

# Generate a classic retro Game Over sound effect
sample_rate = 22050
duration = 1.2
n_samples = int(sample_rate * duration)

with wave.open("gameover.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sample_rate)
    
    for i in range(n_samples):
        t = i / sample_rate
        # Multi-stage descending pitch for dramatic game over effect
        if t < 0.3:
            freq = 320 - t * 150
        elif t < 0.6:
            freq = 240 - (t - 0.3) * 160
        elif t < 0.9:
            freq = 180 - (t - 0.6) * 170
        else:
            freq = 110 - (t - 0.9) * 80
            
        freq = max(40, freq)
        val = math.sin(2 * math.pi * freq * t)
        
        # Envelope: gradual fade out
        envelope = max(0.0, 1.0 - (t / duration) ** 0.8)
        sample = int(val * envelope * 20000)
        sample = max(-32767, min(32767, sample))
        f.writeframes(struct.pack("<h", sample))

print("gameover.wav generated successfully!")
