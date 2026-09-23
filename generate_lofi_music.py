import math
import struct
import wave
import random

SAMPLE_RATE = 44100
BPM = 84
BEAT_DUR = 60.0 / BPM
SUBBEAT_DUR = BEAT_DUR / 4  # 16th note
TOTAL_DURATION = 22.0  # seconds

# Frequencies for Lo-Fi Chords (Hz)
# Chord 1: Fmaj7 (F3, A3, C4, E4)
# Chord 2: Em7 (E3, G3, B3, D4)
# Chord 3: Dm7 (D3, F3, A3, C4)
# Chord 4: Cmaj7 (C3, E3, G3, B3)
CHORDS = [
    [174.61, 220.00, 261.63, 329.63], # Fmaj7
    [164.81, 196.00, 246.94, 293.66], # Em7
    [146.83, 174.61, 220.00, 261.63], # Dm7
    [130.81, 164.81, 196.00, 246.94], # Cmaj7
]
BASS_NOTES = [87.31, 82.41, 73.42, 65.41] # F2, E2, D2, C2

num_samples = int(SAMPLE_RATE * TOTAL_DURATION)
samples = [0.0] * num_samples

def generate_kick(start_sample):
    dur = int(SAMPLE_RATE * 0.18)
    for i in range(dur):
        idx = start_sample + i
        if idx >= num_samples: break
        t = i / SAMPLE_RATE
        freq = 130 * math.exp(-t * 28) + 40
        phase = 2 * math.pi * freq * t
        env = math.exp(-t * 18)
        samples[idx] += 0.45 * math.sin(phase) * env

def generate_snare(start_sample):
    dur = int(SAMPLE_RATE * 0.15)
    random.seed(start_sample)
    for i in range(dur):
        idx = start_sample + i
        if idx >= num_samples: break
        t = i / SAMPLE_RATE
        tone = math.sin(2 * math.pi * 180 * t) * math.exp(-t * 25)
        noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 20)
        samples[idx] += 0.25 * (tone * 0.4 + noise * 0.6)

def generate_hihat(start_sample, accent=1.0):
    dur = int(SAMPLE_RATE * 0.05)
    random.seed(start_sample)
    for i in range(dur):
        idx = start_sample + i
        if idx >= num_samples: break
        t = i / SAMPLE_RATE
        noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 50)
        samples[idx] += 0.08 * accent * noise

# 1. Synthesize Drums (Groovy Lo-Fi Beat)
sample_idx = 0
step = 0
while sample_idx < num_samples:
    beat_in_bar = step % 16
    # Kick on 0, 7, 10
    if beat_in_bar in [0, 7, 10]:
        generate_kick(sample_idx)
    # Snare on 4, 12
    if beat_in_bar in [4, 12]:
        generate_snare(sample_idx)
    # Hihat on every 8th/16th note with swing
    if beat_in_bar % 2 == 0 or random.random() > 0.3:
        accent = 1.2 if beat_in_bar % 4 == 0 else 0.7
        generate_hihat(sample_idx, accent)
    
    step += 1
    # Add subtle swing
    swing_delay = 0.015 if (step % 2 == 1) else 0.0
    sample_idx = int((step * SUBBEAT_DUR + swing_delay) * SAMPLE_RATE)

# 2. Synthesize Chords and Bass
bar_samples = int(BEAT_DUR * 4 * SAMPLE_RATE)
num_bars = int(TOTAL_DURATION / (BEAT_DUR * 4)) + 1

for bar in range(num_bars):
    chord = CHORDS[bar % len(CHORDS)]
    bass_freq = BASS_NOTES[bar % len(BASS_NOTES)]
    bar_start = bar * bar_samples
    
    for i in range(bar_samples):
        idx = bar_start + i
        if idx >= num_samples: break
        t = i / SAMPLE_RATE
        
        # Vinyl wobble (subtle vibrato)
        wobble = math.sin(2 * math.pi * 0.8 * t) * 0.5
        
        # Chord synth (Soft triangle/sine hybrid)
        chord_val = 0.0
        for freq in chord:
            f = freq + wobble
            # Triangle wave
            p = (t * f) % 1.0
            tri = 4.0 * abs(p - 0.5) - 1.0
            # Envelope: gentle attack, long sustain
            env = min(1.0, t / 0.1) * math.exp(-t * 0.35)
            chord_val += tri * env * 0.06
        
        # Sub Bass (pure warm sine)
        bass_phase = 2 * math.pi * bass_freq * t
        bass_env = min(1.0, t / 0.05) * math.exp(-t * 0.4)
        bass_val = math.sin(bass_phase) * bass_env * 0.25
        
        samples[idx] += chord_val + bass_val

# 3. Normalize & Write to WAV file
max_val = max(abs(s) for s in samples) or 1.0
scaling = 28000.0 / max_val

with wave.open("lofi_track.wav", "w") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    
    for s in samples:
        sample_i16 = int(s * scaling)
        sample_i16 = max(-32768, min(32767, sample_i16))
        wav_file.writeframes(struct.pack("<h", sample_i16))

print("Lo-fi music synthesized successfully to lofi_track.wav!")
