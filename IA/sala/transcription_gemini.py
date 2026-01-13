import json
from pathlib import Path
import google.generativeai as genai
from .settings import GEMINI_API_KEY, GEMINI_MODEL
from .diarizer import clean_audio_for_presenter
from .utils_audio import get_audio_duration
import time
from google.api_core import exceptions

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY não definido.")

genai.configure(api_key=GEMINI_API_KEY)

TRANSCRIPT_PROMPT = """
Você recebe um áudio 100% limpo contendo APENAS a fala do apresentador principal de um TCC.
Sua tarefa é transcrever o áudio e classificar o tipo de conteúdo de cada segmento.

REGRAS:
1. Transcreva literalmente. O áudio contém apenas o apresentador.
2. Identifique o "tipo" de conteúdo.

### SOBRE OS CAMPOS DE SAÍDA:
Retorne **apenas JSON válido**, uma lista de objetos, neste formato exato:

[
  {
    "speaker": "apresentador",
    "tipo": "introducao" | "conteudo_tecnico" | "conclusao" | "interacao",
    "texto": "trecho transcrito"
  }
]

### COMO IDENTIFICAR O "tipo":
- "introducao": saudações, apresentação pessoal, explicação do tema ou objetivos.
- "conteudo_tecnico": explicações do corpo principal, referências teóricas, metodologia, análise de resultados.
- "conclusao": encerramento, agradecimentos, frases finais.
- "interacao": (Use "conteudo_tecnico" se não for claro)

### INSTRUÇÕES ADICIONAIS:
- O falante é SEMPRE "apresentador".
- NÃO inclua timestamps, nem formatação adicional.
- Garanta que o JSON seja sintaticamente válido.
"""

def transcribe_with_gemini_long(audio_path: Path, audio_ja_limpo=False):
    try:
        if audio_ja_limpo:
            clean_audio_path = audio_path
            real_presenter_duration = get_audio_duration(audio_path)
        else:
            clean_audio_path, real_presenter_duration = clean_audio_for_presenter(audio_path)
    except Exception as e:
        print(f"[SALA] ERRO NA DIARIZAÇÃO: {e}")
        clean_audio_path = audio_path
        real_presenter_duration = get_audio_duration(audio_path)

    model = genai.GenerativeModel(GEMINI_MODEL)

    with open(clean_audio_path, "rb") as f:
        audio_bytes = f.read()

    if not audio_bytes:
        return "", [], 0.0

    parts = [
        {"mime_type": "audio/wav", "data": audio_bytes},
        TRANSCRIPT_PROMPT,
    ]

    max_retries = 10
    for i in range(max_retries):
        try:
            resp = model.generate_content(
                parts,
                generation_config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                },
            )

            raw = resp.text
            try:
                all_segments = json.loads(raw)
                if not isinstance(all_segments, list):
                    raise ValueError
            except Exception:
                all_segments = [{"speaker": "apresentador", "tipo": "conteudo_tecnico", "texto": raw.strip()}]

            full_text_parts = []
            for s in all_segments:
                s["speaker"] = "apresentador"
                full_text_parts.append(s.get("texto", ""))
                s["inicio"] = 0.0
                s["fim"] = 0.0

            full_text = " ".join(full_text_parts).strip()
            return full_text, all_segments, real_presenter_duration

        except exceptions.ResourceExhausted:
            time.sleep(2 ** i)
            if i == max_retries - 1:
                return "", [], real_presenter_duration
        except Exception:
            return "", [], real_presenter_duration

    return "", [], real_presenter_duration