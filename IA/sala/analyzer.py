import time
import json
import torch
import numpy as np
from pathlib import Path
from .settings import DEVICE
from .paths import SEPARATED_DIR, REPORTS_DIR
from .utils_audio import ffmpeg_extract_audio, get_audio_duration
from .transcription_gemini import transcribe_with_gemini_long
from .language import AutoLanguageAnalyzer
from .audio_features import analyze_audio_features
from .fusion import fuse_multimodal
from .metrics import calculate_wpm, compute_tangencia, score_velocidade, calculate_final
from .feedback_gemini import generate_feedback
from .diarizer import clean_audio_for_presenter

torch.set_float32_matmul_precision("high")
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.cuda.set_device(0)
    torch.cuda.empty_cache()

TIPOS_SEM_DIARIZACAO = {
    "palestra_tecnica",
    "palestra_motivacional",
    "videoaula",
    "explicacao_escolar",
}

def stable_round(x, decimals=2):
    return float(f"{x:.{decimals}f}")

class SalaAnalyzer:
    def __init__(self):
        print(f"GPU ativa: {DEVICE}")

    def process(self, video_path, theme, tipo_discurso, save_json=True, contexto_apresentacao=None):
        t0 = time.time()
        video_path = Path(video_path)

        SEPARATED_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        audio_path = SEPARATED_DIR / f"{video_path.stem}_mono.wav"
        ffmpeg_extract_audio(video_path, audio_path, sr=16000)
        dur_sec_total = get_audio_duration(audio_path)

        usar_diarizacao = tipo_discurso not in TIPOS_SEM_DIARIZACAO

        if usar_diarizacao:
            clean_path, presenter_duration_sec = clean_audio_for_presenter(audio_path)
            presenter_text, segments, _ = transcribe_with_gemini_long(clean_path, audio_ja_limpo=True)
            audio_for_analysis = clean_path
        else:
            presenter_text, segments, presenter_duration_sec = transcribe_with_gemini_long(audio_path, audio_ja_limpo=True)
            audio_for_analysis = audio_path

        text = " ".join(presenter_text.split()).replace(".", "").replace(",", "")
        theme_clean = " ".join(theme.split()).lower()

        wpm = calculate_wpm(text, presenter_duration_sec)
        tang_sim = compute_tangencia(text, theme_clean)

        text_metrics = AutoLanguageAnalyzer().analyze(text=text)
        audio_metrics = analyze_audio_features(audio_for_analysis)
        fused = fuse_multimodal(text_metrics, audio_metrics)

        scores = {
            "velocidade": stable_round(score_velocidade(wpm), 2),
            "tangencia": stable_round(max(0, min(10, tang_sim * 10)), 2),
            "clareza": stable_round(max(0, min(10, fused["clarity"] * 10)), 2),
            "nervosismo": stable_round(max(0, min(10, (1 - fused["human_nervousness"]) * 10)), 2),
            "prosodia": stable_round(max(0, min(10, fused["prosody_proxy"] * 10)), 2),
        }

        lang = {
            "token_diversity": float(text_metrics["token_diversity"]),
            "semantic_redundancy": float(text_metrics["semantic_redundancy"]),
            "clarity_text": float(text_metrics["clarity_text"]),
            "prosody_text": float(text_metrics["prosody_text"]),
            "nervous_textual": float(text_metrics["nervous_textual"]),
            "prosody_proxy": float(fused["prosody_proxy"]),
            "human_nervousness": float(fused["human_nervousness"]),
            "clarity": float(fused["clarity"]),
        }

        acoustic = {
            "prosody_audio": float(audio_metrics["prosody_audio"]),
            "human_nervousness_audio": float(audio_metrics["human_nervousness_audio"]),
            "clarity_audio": float(audio_metrics["clarity_audio"]),
            "jitter": float(audio_metrics["jitter"]),
            "shimmer": float(audio_metrics["shimmer"]),
            "hnr": float(audio_metrics["hnr"]),
            "energy_var": float(audio_metrics["energy_var"]),
            "pause_rate": float(audio_metrics["pause_rate"]),
        }

        final_score, contribs = calculate_final(scores, tipo_discurso)

        report = {
            "input": str(video_path),
            "audio": str(audio_path),
            "duration_total": stable_round(dur_sec_total, 2),
            "duration_presenter_real": stable_round(presenter_duration_sec, 2),
            "segmentos_totais": len(segments),
            "segmentos_usados": len(segments),
            "analisado": "apresentador" if usar_diarizacao else "audio_completo",
            "text": presenter_text,
            "wpm_real": stable_round(wpm, 2),
            "tangencia_sim": stable_round(tang_sim, 4),
            "scores": scores,
            "scores_contribuicoes": contribs,
            "final_score": stable_round(final_score, 2),
            "linguagem": lang,
            "acustica": acoustic,
            "tema_fornecido": theme,
            "tipo_discurso": tipo_discurso,
            "tempo_execucao": stable_round(time.time() - t0, 2),
            "contexto_apresentacao": contexto_apresentacao or "",
        }

        report["feedback_gemini"] = generate_feedback(report)

        if save_json:
            report_path = REPORTS_DIR / f"SALA_{video_path.stem}_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print("[SALA] Relatório salvo", flush=True)

        return report