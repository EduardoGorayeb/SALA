import numpy as np

def fuse_multimodal(text_metrics, audio_metrics):
    prosody_text = text_metrics["prosody_text"]
    clarity_text = text_metrics["clarity_text"]
    nervous_textual = text_metrics["nervous_textual"]

    prosody_audio = audio_metrics["prosody_audio"]
    clarity_audio = audio_metrics["clarity_audio"]
    nervous_audio = audio_metrics["human_nervousness_audio"]

    prosody_proxy = float(np.clip(0.45 * prosody_text + 0.55 * prosody_audio, 0.0, 1.0))
    clarity = float(np.clip(0.55 * clarity_text + 0.45 * clarity_audio, 0.0, 1.0))
    human_nervousness = float(np.clip(0.40 * nervous_textual + 0.60 * nervous_audio, 0.0, 1.0))

    return {
        "prosody_proxy": prosody_proxy,
        "clarity": clarity,
        "human_nervousness": human_nervousness
    }