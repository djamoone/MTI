"""
build_sounds.py
===============
Procedurally generates the game's sound effects as WAV files in
assets/sounds/. No external assets needed - everything is synthesized
with numpy so the project stays self-contained.

Run from the project root:
    python scripts/build_sounds.py
"""

import os
import math
import wave
import struct
import numpy as np

HERE    = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OUT     = os.path.join(PROJECT, "assets", "sounds")

SR = 22050   # sample rate


def save_wav(name, samples):
    """Write a mono float [-1, 1] array to a 16-bit PCM WAV."""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"  {name}: {len(samples)/SR:.2f}s")


def adsr(n, a=0.005, d=0.05, s=0.4, r=0.05, sr=SR):
    """Simple ADSR envelope of length n samples."""
    env = np.zeros(n)
    a_s = int(a * sr); d_s = int(d * sr); r_s = int(r * sr)
    a_s = min(a_s, n); d_s = min(d_s, n - a_s)
    s_s = max(0, n - a_s - d_s - r_s); r_s = min(r_s, n - a_s - d_s - s_s)
    i = 0
    if a_s:
        env[i:i+a_s] = np.linspace(0, 1, a_s); i += a_s
    if d_s:
        env[i:i+d_s] = np.linspace(1, s, d_s); i += d_s
    if s_s:
        env[i:i+s_s] = s; i += s_s
    if r_s:
        env[i:i+r_s] = np.linspace(s, 0, r_s)
    return env


def t(len_s):
    return np.linspace(0, len_s, int(SR * len_s), endpoint=False)


# ------------------------------------------------------------------

def shoot():
    """Short bright laser pew: descending sine + click."""
    dur = 0.18
    n = int(SR * dur)
    env = adsr(n, a=0.002, d=0.04, s=0.2, r=0.08)
    freq = 1400 * np.exp(-t(dur) * 8) + 350
    wave_ = 0.6 * np.sin(2 * np.pi * np.cumsum(freq) / SR)
    noise = 0.2 * np.random.uniform(-1, 1, n) * np.exp(-t(dur) * 20)
    save_wav("shoot.wav", env * (wave_ + noise))


def hit():
    """Wet impact: low thump + metallic noise."""
    dur = 0.22
    n = int(SR * dur)
    env = adsr(n, a=0.001, d=0.05, s=0.0, r=0.05)
    low = 0.7 * np.sin(2 * np.pi * 90 * t(dur)) * np.exp(-t(dur) * 14)
    noise = 0.4 * np.random.uniform(-1, 1, n) * np.exp(-t(dur) * 18)
    save_wav("hit.wav", env * (low + noise))


def explosion():
    """Bigger explosion: rumble + bright noise burst."""
    dur = 0.55
    n = int(SR * dur)
    env = adsr(n, a=0.003, d=0.15, s=0.2, r=0.25)
    low = 0.6 * np.sin(2 * np.pi * 55 * t(dur)) * np.exp(-t(dur) * 5)
    mid = 0.3 * np.sin(2 * np.pi * 180 * t(dur)) * np.exp(-t(dur) * 9)
    noise = 0.55 * np.random.uniform(-1, 1, n) * np.exp(-t(dur) * 6)
    save_wav("explosion.wav", env * (low + mid + noise))


def pickup():
    """Sparkly arpeggio: ascending two notes."""
    dur = 0.32
    n = int(SR * dur)
    env = adsr(n, a=0.003, d=0.04, s=0.6, r=0.10)
    notes = [523, 784]   # C5 -> G5
    seg = n // 2
    out = np.zeros(n)
    for k, f in enumerate(notes):
        s = k * seg
        e = s + seg
        out[s:e] += 0.5 * np.sin(2 * np.pi * f * t(dur)[:seg])
    save_wav("pickup.wav", env * out)


def levelup():
    """Three ascending notes - fanfare."""
    dur = 0.55
    n = int(SR * dur)
    env = adsr(n, a=0.005, d=0.05, s=0.6, r=0.18)
    notes = [523, 659, 784]   # C5 -> E5 -> G5
    seg = n // 3
    out = np.zeros(n)
    for k, f in enumerate(notes):
        s = k * seg
        e = s + seg
        out[s:e] += 0.5 * np.sin(2 * np.pi * f * t(dur)[:seg])
    save_wav("levelup.wav", env * out)


def gameover():
    """Descending sad trombone."""
    dur = 1.1
    n = int(SR * dur)
    env = adsr(n, a=0.01, d=0.15, s=0.5, r=0.45)
    freq = 400 * np.exp(-t(dur) * 1.7) + 80
    wave_ = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    save_wav("gameover.wav", 0.55 * env * wave_)


def victory():
    """Bright triumphant chord."""
    dur = 1.2
    n = int(SR * dur)
    env = adsr(n, a=0.02, d=0.1, s=0.7, r=0.5)
    chord = [523, 659, 784, 1047]   # C major
    out = np.zeros(n)
    for f in chord:
        out += 0.25 * np.sin(2 * np.pi * f * t(dur))
    save_wav("victory.wav", env * out)


def menu_select():
    """UI click for menu / pause actions."""
    dur = 0.10
    n = int(SR * dur)
    env = adsr(n, a=0.001, d=0.02, s=0.0, r=0.03)
    wave_ = 0.4 * np.sin(2 * np.pi * 880 * t(dur))
    save_wav("menu_select.wav", env * wave_)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("Generating sounds in:", OUT)
    shoot()
    hit()
    explosion()
    pickup()
    levelup()
    gameover()
    victory()
    menu_select()
    print("Done.")
