import librosa
import numpy as np

def _safe_mean(x):
    if len(x) == 0:
        return 0.0
    return float(np.nanmean(x))

def extract_pitch(y, sr):
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=50,
        fmax=600,
        frame_length=2048,
        hop_length=256
    )
    f0 = np.nan_to_num(f0, nan=0.0)
    voiced = f0[f0 > 0]
    return voiced

def compute_jitter(pitch):
    if len(pitch) < 3:
        return 0.5
    diffs = np.abs(np.diff(pitch))
    jitter = np.mean(diffs / (pitch[:-1] + 1e-6))
    return float(np.clip(jitter, 0, 1))

def compute_shimmer(y, sr):
    amp = np.abs(librosa.stft(y))
    env = np.mean(amp, axis=0)
    if len(env) < 3:
        return 0.5
    diffs = np.abs(np.diff(env))
    shimmer = np.mean(diffs / (env[:-1] + 1e-6))
    return float(np.clip(shimmer, 0, 1))

def compute_hnr(y, sr):
    y_h = librosa.effects.harmonic(y)
    y_p = librosa.effects.percussive(y)
    h = np.mean(np.abs(y_h))
    n = np.mean(np.abs(y_p)) + 1e-6
    hnr = h / n
    hnr = hnr / (hnr + 1)
    return float(np.clip(hnr, 0, 1))

def compute_energy_variation(y, sr):
    rms = librosa.feature.rms(y=y)[0]
    if len(rms) < 3:
        return 0.3
    v = np.std(rms)
    v = float(np.clip(v * 10, 0, 1))
    return v

def compute_pause_rate(y, sr):
    rms = librosa.feature.rms(y=y)[0]
    thr = np.percentile(rms, 20)
    sil = rms < thr
    rate = np.mean(sil)
    return float(np.clip(rate, 0, 1))

def compute_prosody(pitch, hnr, energy_var):
    p_std = np.std(pitch) / 100 if len(pitch) > 1 else 0
    p_std = float(np.clip(p_std, 0, 1))
    score = (0.45 * p_std) + (0.30 * hnr) + (0.25 * energy_var)
    return float(np.clip(score, 0, 1))

def compute_nervousness(jitter, shimmer, pause_rate, energy_var):
    score = (
        jitter * 0.35 +
        shimmer * 0.25 +
        pause_rate * 0.25 +
        (1 - energy_var) * 0.15
    )
    return float(np.clip(score, 0, 1))

def compute_acoustic_clarity(hnr, energy_var):
    c = (0.65 * hnr) + (0.35 * energy_var)
    return float(np.clip(c, 0, 1))

def analyze_audio_features(audio_path):
    y, sr = librosa.load(str(audio_path), sr=16000, mono=True)

    pitch = extract_pitch(y, sr)
    jitter = compute_jitter(pitch)
    shimmer = compute_shimmer(y, sr)
    hnr = compute_hnr(y, sr)
    energy_var = compute_energy_variation(y, sr)
    pause_rate = compute_pause_rate(y, sr)

    prosody = compute_prosody(pitch, hnr, energy_var)
    nervous = compute_nervousness(jitter, shimmer, pause_rate, energy_var)
    clarity = compute_acoustic_clarity(hnr, energy_var)

    return {
        "prosody_audio": prosody,
        "human_nervousness_audio": nervous,
        "clarity_audio": clarity,
        "jitter": jitter,
        "shimmer": shimmer,
        "hnr": hnr,
        "energy_var": energy_var,
        "pause_rate": pause_rate
    }