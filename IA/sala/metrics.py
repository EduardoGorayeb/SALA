import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util
from .settings import DEVICE

np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

torch.set_float32_matmul_precision("high")
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

_model_tangencia = None


def get_tangencia_model():
    global _model_tangencia
    if _model_tangencia is None:
        _model_tangencia = SentenceTransformer(
            "intfloat/multilingual-e5-large",
            device=DEVICE,
            trust_remote_code=True
        )
    return _model_tangencia


def clamp(x, a, b):
    return max(a, min(x, b))


def calculate_wpm(text: str, duration_sec: float) -> float:
    words = len(text.split())
    if duration_sec <= 0:
        return 0.0
    return (words / duration_sec) * 60.0


def compute_tangencia(text: str, theme: str) -> float:
    if not text or not theme:
        return 0.0
    model = get_tangencia_model()
    embs = model.encode(
        [text, theme],
        convert_to_tensor=True,
        normalize_embeddings=True
    )
    sim = util.cos_sim(embs[0], embs[1])
    val = float(sim.item())
    val = max(0.0, min(1.0, val))
    return val


def score_velocidade(wpm):
    if 125 <= wpm <= 150:
        return 10.0
    if 110 <= wpm < 125:
        return 7 + (wpm - 110) * (3 / 15)
    if 150 < wpm <= 165:
        return 10 - (wpm - 150) * (3 / 15)
    if 90 <= wpm < 110:
        return 5 + (wpm - 90) * (2 / 20)
    if 165 < wpm <= 185:
        return 7 - (wpm - 165) * (2 / 20)
    if wpm < 90:
        return max(0, wpm * 0.05)
    if wpm > 185:
        return max(0, 10 - (wpm - 185) * 0.1)
    return 0.0


def norm10(x):
    if x is None:
        return 0.0
    return clamp(x / 10.0, 0.0, 1.0)


def aplicar_rigor(score_base, tipo):
    fatores = {
        "tcc": 0.82,
        "explicacao_escolar": 1.10,
        "palestra_tecnica": 0.95,
        "videoaula": 0.95,
        "palestra_motivacional": 1.02,
        "pitch_comercial": 1.00,
        "pitch_startup": 1.00,
        "livre": 1.00,
    }
    f = fatores.get(tipo, 1.00)
    return clamp(score_base * f, 0.0, 1.0)


def curva_tcc(m):
    v = norm10(m["velocidade"])
    t = norm10(m["tangencia"])
    c = norm10(m["clareza"])
    n = norm10(m["nervosismo"])
    p = norm10(m["prosodia"])
    score_base = (
        v * 0.10 +
        t * 0.30 +
        c * 0.30 +
        n * 0.15 +
        p * 0.15
    )
    score_base = clamp(score_base, 0.0, 1.0)
    score_rigor = aplicar_rigor(score_base, "tcc")
    final = clamp(score_rigor * 10.0, 0.0, 10.0)
    contrib = {
        "velocidade": round(v * 0.10, 3),
        "tangencia": round(t * 0.30, 3),
        "clareza": round(c * 0.30, 3),
        "nervosismo": round(n * 0.15, 3),
        "prosodia": round(p * 0.15, 3),
    }
    return final, contrib


def curva_escolar(m):
    v = norm10(m["velocidade"])
    t = norm10(m["tangencia"])
    c = norm10(m["clareza"])
    n = norm10(m["nervosismo"])
    p = norm10(m["prosodia"])
    score_base = (
        v * 0.20 +
        t * 0.30 +
        c * 0.20 +
        n * 0.15 +
        p * 0.15
    )
    score_base = clamp(score_base, 0.0, 1.0)
    score_rigor = aplicar_rigor(score_base, "explicacao_escolar")
    final = clamp(score_rigor * 10.0, 0.0, 10.0)
    contrib = {
        "velocidade": round(v * 0.20, 3),
        "tangencia": round(t * 0.30, 3),
        "clareza": round(c * 0.20, 3),
        "nervosismo": round(n * 0.15, 3),
        "prosodia": round(p * 0.15, 3),
    }
    return final, contrib


def curva_palestra_tecnica(m):
    v = norm10(m["velocidade"])
    t = norm10(m["tangencia"])
    c = norm10(m["clareza"])
    n = norm10(m["nervosismo"])
    p = norm10(m["prosodia"])
    score_base = (
        v * 0.10 +
        t * 0.35 +
        c * 0.35 +
        n * 0.10 +
        p * 0.10
    )
    score_base = clamp(score_base, 0.0, 1.0)
    score_rigor = aplicar_rigor(score_base, "palestra_tecnica")
    final = clamp(score_rigor * 10.0, 0.0, 10.0)
    contrib = {
        "velocidade": round(v * 0.10, 3),
        "tangencia": round(t * 0.35, 3),
        "clareza": round(c * 0.35, 3),
        "nervosismo": round(n * 0.10, 3),
        "prosodia": round(p * 0.10, 3),
    }
    return final, contrib


def curva_palestra_motivacional(m):
    v = norm10(m["velocidade"])
    t = norm10(m["tangencia"])
    c = norm10(m["clareza"])
    n = norm10(m["nervosismo"])
    p = norm10(m["prosodia"])
    score_base = (
        v * 0.15 +
        t * 0.10 +
        c * 0.30 +
        n * 0.05 +
        p * 0.40
    )
    score_base = clamp(score_base, 0.0, 1.0)
    score_rigor = aplicar_rigor(score_base, "palestra_motivacional")
    final = clamp(score_rigor * 10.0, 0.0, 10.0)
    contrib = {
        "velocidade": round(v * 0.15, 3),
        "tangencia": round(t * 0.10, 3),
        "clareza": round(c * 0.30, 3),
        "nervosismo": round(n * 0.05, 3),
        "prosodia": round(p * 0.40, 3),
    }
    return final, contrib


def curva_pitch(m):
    v = norm10(m["velocidade"])
    t = norm10(m["tangencia"])
    c = norm10(m["clareza"])
    n = norm10(m["nervosismo"])
    p = norm10(m["prosodia"])
    score_base = (
        v * 0.30 +
        t * 0.10 +
        c * 0.20 +
        n * 0.05 +
        p * 0.35
    )
    score_base = clamp(score_base, 0.0, 1.0)
    score_rigor = aplicar_rigor(score_base, "pitch_comercial")
    final = clamp(score_rigor * 10.0, 0.0, 10.0)
    contrib = {
        "velocidade": round(v * 0.30, 3),
        "tangencia": round(t * 0.10, 3),
        "clareza": round(c * 0.20, 3),
        "nervosismo": round(n * 0.05, 3),
        "prosodia": round(p * 0.35, 3),
    }
    return final, contrib


def curva_livre(m):
    v = norm10(m["velocidade"])
    t = norm10(m["tangencia"])
    c = norm10(m["clareza"])
    n = norm10(m["nervosismo"])
    p = norm10(m["prosodia"])
    score_base = (
        v * 0.20 +
        t * 0.20 +
        c * 0.20 +
        n * 0.20 +
        p * 0.20
    )
    score_base = clamp(score_base, 0.0, 1.0)
    score_rigor = aplicar_rigor(score_base, "livre")
    final = clamp(score_rigor * 10.0, 0.0, 10.0)
    contrib = {
        "velocidade": round(v * 0.20, 3),
        "tangencia": round(t * 0.20, 3),
        "clareza": round(c * 0.20, 3),
        "nervosismo": round(n * 0.20, 3),
        "prosodia": round(p * 0.20, 3),
    }
    return final, contrib


def calculate_final(m, tipo):
    mapa = {
        "tcc": curva_tcc,
        "palestra_tecnica": curva_palestra_tecnica,
        "videoaula": curva_palestra_tecnica,
        "palestra_motivacional": curva_palestra_motivacional,
        "pitch_comercial": curva_pitch,
        "pitch_startup": curva_pitch,
        "explicacao_escolar": curva_escolar,
        "livre": curva_livre,
    }
    if tipo not in mapa:
        tipo = "livre"
    return mapa[tipo](m)