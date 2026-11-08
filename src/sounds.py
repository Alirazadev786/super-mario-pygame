"""
Synthesized sound effects using numpy for Super Mario (no external audio files needed).
"""
import numpy as np
import pygame

_sounds = {}
_initialized = False

def _synth(freq, dur, wave='sine', vol=0.5, decay=True, freq_end=None):
    sr = 22050
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    if freq_end is None:
        freq_end = freq
    f = np.linspace(freq, freq_end, n)
    phase = 2 * np.pi * np.cumsum(f) / sr
    if wave == 'sine':
        w = np.sin(phase)
    elif wave == 'square':
        w = np.sign(np.sin(phase))
    elif wave == 'triangle':
        w = 2 * np.abs(2 * (phase / (2*np.pi) - np.floor(phase / (2*np.pi) + 0.5))) - 1
    elif wave == 'saw':
        w = 2 * (phase / (2*np.pi) - np.floor(phase / (2*np.pi) + 0.5))
    else:
        w = np.sin(phase)
    if decay:
        env = np.exp(-3 * t / dur)
    else:
        env = np.ones(n)
    data = (w * env * vol * 32767).astype(np.int16)
    data = np.column_stack([data, data])
    return pygame.sndarray.make_sound(data)

def init():
    global _initialized
    if _initialized:
        return
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    except Exception:
        return
    # Classic Mario-style sounds
    _sounds['jump'] = _synth(300, 0.15, 'square', 0.3, freq_end=600)
    _sounds['coin'] = _synth(988, 0.08, 'square', 0.3, freq_end=1319)
    _sounds['powerup'] = _synth(523, 0.12, 'triangle', 0.35, freq_end=784)
    _sounds['powerup2'] = _synth(784, 0.12, 'triangle', 0.35, freq_end=1046)
    _sounds['stomp'] = _synth(200, 0.1, 'saw', 0.4, freq_end=80)
    _sounds['death'] = _synth(400, 0.5, 'saw', 0.4, freq_end=80)
    _sounds['brick'] = _synth(150, 0.1, 'square', 0.35, freq_end=60)
    _sounds['fireball'] = _synth(600, 0.2, 'saw', 0.3, freq_end=200)
    _sounds['star'] = _synth(600, 0.1, 'triangle', 0.3, freq_end=1200)
    _sounds['win'] = _synth(523, 0.15, 'triangle', 0.4, freq_end=523)
    _sounds['win2'] = _synth(659, 0.15, 'triangle', 0.4, freq_end=659)
    _sounds['win3'] = _synth(784, 0.2, 'triangle', 0.4, freq_end=784)
    _sounds['win4'] = _synth(1046, 0.3, 'triangle', 0.4, freq_end=1046)
    _sounds['gameover'] = _synth(300, 0.4, 'saw', 0.4, freq_end=100)
    _sounds['oneup'] = _synth(400, 0.1, 'square', 0.35, freq_end=800)
    _sounds['oneup2'] = _synth(800, 0.1, 'square', 0.35, freq_end=1600)
    _initialized = True

def play(name):
    if name in _sounds:
        _sounds[name].play()

def stop_all():
    for s in _sounds.values():
        s.stop()