import torch
from pathlib import Path
from pydub import AudioSegment
from pyannote.audio import Pipeline
from .settings import DEVICE, HF_TOKEN
import tempfile
import librosa

if not HF_TOKEN:
    print("[SALA] ALERTA: HF_TOKEN não definido. A diarização pode falhar se o modelo for privado.")

_pipeline = None

def get_diarization_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            print(f"[SALA] Carregando pipeline de diarização no {DEVICE}...", flush=True)
            _pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1").to(
                torch.device(DEVICE)
            )
            print("[SALA] Pipeline de diarização carregado.", flush=True)
        except Exception as e:
            print(f"[SALA] ERRO CRÍTICO ao carregar pyannote: {e}")
            return None
    return _pipeline

def _get_annotation_obj(diarization):
    if hasattr(diarization, "speaker_diarization"):
        return diarization.speaker_diarization
    if hasattr(diarization, "exclusive_speaker_diarization"):
        return diarization.exclusive_speaker_diarization
    if hasattr(diarization, "itertracks"):
        return diarization
    if hasattr(diarization, "annotation"):
        return diarization.annotation
    if isinstance(diarization, dict):
        if "annotation" in diarization:
            return diarization["annotation"]
        if "diarization" in diarization:
            return diarization["diarization"]
    raise RuntimeError("Formato desconhecido do retorno de diarização.")

def clean_audio_for_presenter(audio_path: Path):
    pipeline = get_diarization_pipeline()
    if pipeline is None:
        raise RuntimeError("Falha ao carregar a pipeline de diarização.")

    print("[SALA] Iniciando diarização...", flush=True)
    try:
        y, sr = librosa.load(str(audio_path), sr=16000, mono=True)
        audio_dict = {"waveform": torch.tensor(y).unsqueeze(0), "sample_rate": sr}
        diarization = pipeline(audio_dict, min_speakers=1, max_speakers=5)
    except Exception as e:
        print(f"[SALA] Erro durante a diarização: {e}")
        original = AudioSegment.from_file(audio_path)
        return audio_path, original.duration_seconds

    try:
        annotation = _get_annotation_obj(diarization)
    except Exception as e:
        print(f"[SALA] Falha ao obter annotation: {e}")
        original = AudioSegment.from_file(audio_path)
        return audio_path, original.duration_seconds

    speaker_duration = {}
    turns = []

    for turn, _, speaker in annotation.itertracks(yield_label=True):
        duration = turn.end - turn.start
        speaker_duration[speaker] = speaker_duration.get(speaker, 0.0) + duration
        turns.append((turn, speaker))

    if not speaker_duration:
        original = AudioSegment.from_file(audio_path)
        return audio_path, original.duration_seconds

    presenter_label = max(speaker_duration, key=speaker_duration.get)
    presenter_total_duration_sec = speaker_duration[presenter_label]

    original_audio = AudioSegment.from_file(audio_path)
    presenter_segments = AudioSegment.empty()

    for turn, speaker in turns:
        if speaker == presenter_label:
            start_ms = turn.start * 1000
            end_ms = turn.end * 1000
            presenter_segments += original_audio[start_ms:end_ms]

    if len(presenter_segments) == 0:
        original = AudioSegment.from_file(audio_path)
        return audio_path, original.duration_seconds

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        clean_audio_path = Path(f.name)

    presenter_segments.export(clean_audio_path, format="wav")
    print(f"[SALA] Áudio limpo salvo em: {clean_audio_path}", flush=True)

    return clean_audio_path, presenter_total_duration_sec