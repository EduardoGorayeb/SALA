import numpy as np
import nltk
import re
from sentence_transformers import SentenceTransformer, util
from .settings import DEVICE

for resource in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource)

class AutoLanguageAnalyzer:
    def __init__(self, model_name="intfloat/multilingual-e5-large"):
        self.model = SentenceTransformer(model_name, device=DEVICE, trust_remote_code=True)

    def _clean_text(self, text: str):
        text_clean = re.sub(r"[^a-zà-ú0-9\s'-]", " ", text.lower())
        text_clean = re.sub(r"\s+", " ", text_clean).strip()
        return text_clean

    def _analyze_text(self, text: str):
        text_clean = self._clean_text(text)
        tokens = text_clean.split()
        total_tokens = len(tokens)

        if total_tokens < 20:
            return {
                "token_diversity": 0.0,
                "semantic_redundancy": 1.0,
                "clarity_text": 0.0,
                "prosody_text": 0.0,
                "nervous_textual": 0.0
            }

        vocab = len(set(tokens))
        token_diversity = vocab / total_tokens

        sentences = [s.strip() for s in nltk.sent_tokenize(text) if len(s.strip().split()) > 4]

        if len(sentences) < 3:
            base_clarity = token_diversity * 0.3
            base_prosody = 0.3
            nervous_textual = float(np.clip(1 - base_prosody, 0, 1))
            return {
                "token_diversity": float(token_diversity),
                "semantic_redundancy": 1.0,
                "clarity_text": float(base_clarity),
                "prosody_text": float(base_prosody),
                "nervous_textual": float(nervous_textual)
            }

        embs = self.model.encode(sentences, convert_to_tensor=True, normalize_embeddings=True)
        sim_matrix = util.cos_sim(embs, embs).cpu().numpy()

        off_diag = sim_matrix[~np.eye(sim_matrix.shape[0], dtype=bool)]
        semantic_redundancy = float(off_diag.mean())
        semantic_drift = float(off_diag.std())

        sent_lengths = np.array([len(s.split()) for s in sentences])
        length_var = np.std(sent_lengths) / (np.mean(sent_lengths) + 1e-6)

        prosody_raw = (0.4 * length_var) + (0.6 * (1 - semantic_drift))
        prosody_text = float(np.clip(prosody_raw * 0.6, 0, 1))

        clarity_raw = (token_diversity * 0.25) + ((1 - semantic_drift) * 0.75)
        clarity_text = float(np.clip(clarity_raw * 0.7, 0, 1))

        texto_baixo = text.lower()
        fillers = re.findall(r"\b(ah|eh|né|tipo|hã|hum|ééé|perdão|desculpa)\b", texto_baixo)
        tokens2 = re.findall(r"\b[\wà-ú'-]+\b", texto_baixo)
        total_tokens2 = max(1, len(tokens2))
        filler_rate = len(fillers) / total_tokens2

        rep_pairs = 0
        for i in range(1, len(tokens2)):
            if tokens2[i] == tokens2[i-1]:
                rep_pairs += 1
        rep_rate = rep_pairs / total_tokens2

        nervous_textual = float(np.clip((filler_rate * 3.0 + rep_rate * 5.0), 0.0, 1.0))

        return {
            "token_diversity": float(token_diversity),
            "semantic_redundancy": float(semantic_redundancy),
            "clarity_text": float(clarity_text),
            "prosody_text": float(prosody_text),
            "nervous_textual": float(nervous_textual)
        }

    def analyze(self, text: str):
        return self._analyze_text(text)