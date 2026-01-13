import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

class SpeakerSelector:
    def __init__(self, model_name="intfloat/multilingual-e5-large"):
        self.model = SentenceTransformer(model_name)

    def select_presenter(self, segments):
        texts = [s["texto"] for s in segments if s.get("texto")]
        if not texts:
            return segments
        embs = self.model.encode(texts, normalize_embeddings=True)
        clustering = DBSCAN(eps=0.28, min_samples=2, metric="cosine").fit(embs)
        labels = clustering.labels_
        if (labels >= 0).sum() == 0:
            return segments
        dur_by_label = {}
        idx = 0
        for seg in segments:
            if seg.get("texto"):
                label = labels[idx]
                dur = float(seg.get("fim", 0) - seg.get("inicio", 0))
                dur_by_label[label] = dur_by_label.get(label, 0.0) + dur
                idx += 1
        valid_labels = {k: v for k, v in dur_by_label.items() if k >= 0}
        if not valid_labels:
            return segments
        main_label = max(valid_labels, key=valid_labels.get)
        presenter_segments = []
        idx = 0
        for seg in segments:
            if seg.get("texto"):
                label = labels[idx]
                if label == main_label:
                    presenter_segments.append(seg)
                idx += 1
        total_duration = sum(s.get("fim", 0) - s.get("inicio", 0) for s in segments)
        presenter_duration = sum(s.get("fim", 0) - s.get("inicio", 0) for s in presenter_segments)
        if total_duration > 0 and presenter_duration / total_duration < 0.45:
            presenter_segments = segments[: int(len(segments) * 0.55)]
        return presenter_segments

def estimate_segment_times(segments, total_duration):
    word_counts = [len(s.get("texto", "").split()) for s in segments]
    total_words = sum(word_counts) if sum(word_counts) > 0 else 1
    current = 0.0
    for seg, wc in zip(segments, word_counts):
        seg_dur = total_duration * (wc / total_words)
        seg["inicio"] = current
        seg["fim"] = current + seg_dur
        current += seg_dur
    return segments