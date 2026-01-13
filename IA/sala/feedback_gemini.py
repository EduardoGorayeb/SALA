import json
import google.generativeai as genai
from .settings import GEMINI_API_KEY, GEMINI_MODEL
import time
from google.api_core import exceptions

def generate_feedback(report: dict):
    if not GEMINI_API_KEY:
        return {
            "principais_falhas": [],
            "acoes_curto_prazo": [],
            "resumo_geral": "Configure a chave GEMINI_API_KEY.",
            "vicios_linguagem": [],
        }

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    report["transcricao"] = report.get("text", "")
    contexto = report.get("contexto_apresentacao") or ""
    if contexto.strip():
        report["contexto"] = contexto

    bloco_contexto = ""
    if contexto.strip():
        bloco_contexto = (
            """
O usuário forneceu um CONTEXTO opcional explicando sobre o tema da apresentação. 
Use este contexto para compreender conceitos específicos, evitar falsas críticas de tangência,
entender o propósito real do conteúdo e interpretar corretamente temas técnicos ou internos.
Jamais ignore o contexto; ele faz parte da avaliação.
"""
        )

    prompt = (
        """
Você é um avaliador altamente especializado em oratória, ritmo, clareza verbal, estrutura comunicativa e desempenho vocal.
Você irá analisar um relatório técnico do sistema SALA, contendo métricas objetivas, dados acústicos, dados linguísticos,
velocidade de fala, prosódia, nervosismo, tangência ao tema, WPM e a transcrição completa.

"""
        + bloco_contexto
        + 
        """
A adaptação deve seguir o tipo de apresentação informado:

TCC:
- Exige maior rigor técnico.
- Clareza e prosódia têm importância alta.
- Ritmo rápido pode prejudicar bastante.
- Repetições simples impactam formalidade.

Explicação escolar:
- Deve ser mais leve e acessível.
- Uma pequena dose de nervosismo é aceitável.
- Vocabulário simples não prejudica a nota.
- Velocidade um pouco maior não é uma falha grave.

Palestra técnica:
- Importância altíssima na clareza e precisão.
- Nervosismo importa pouco desde que não prejudique a técnica.
- Tangência é extremamente relevante.
- Ritmo pode ser mais livre desde que inteligível.

Palestra motivacional:
- Prosódia, emoção e ritmo importam mais.
- Nervosismo só é negativo quando atrapalha a expressividade.
- Clareza importa, mas emoção pesa mais.

Pitch comercial ou pitch startup:
- Comunicação rápida é comum.
- Leve nervosismo não penaliza.
- Clareza e objetividade são essenciais.
- Prosódia e impacto são mais importantes do que velocidade.

Livre:
- Não assuma regras rígidas.
- Avaliação equilibrada e neutra.

INSTRUÇÕES PARA O FEEDBACK:

1. Gerar APENAS um JSON contendo:
- "principais_falhas": até 5 falhas reais (não inventar nenhuma).
- "acoes_curto_prazo": até 5 ações práticas aplicáveis imediatamente.
- "resumo_geral": texto único (8–10 linhas) citando as métricas, o tipo e o contexto (se existir).
- "vicios_linguagem": vícios REAIS identificados na transcrição (não inventar nada).

2. Usar somente fatos da transcrição, métricas e contexto.

3. Identificar vícios reais:
"a gente", "né", "tipo", "ééé", "ah", "o o", "da da", "eu eu", "perdão", "desculpa", repetições desnecessárias, gaguejos.

4. Considerar fortemente:
clareza, prosódia, nervosismo, tangência, velocidade, redundância, diversidade de vocabulário, hesitações.

5. Se existir contexto, ele deve influenciar a interpretação de termos técnicos, temas raros ou projetos específicos.

A resposta DEVE ser SOMENTE o JSON final.

Agora analise o relatório abaixo:
"""
        + json.dumps(report, ensure_ascii=False)
    )

    max_retries = 10
    resp = None

    for i in range(max_retries):
        try:
            resp = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                },
            )
            break
        except exceptions.ResourceExhausted:
            time.sleep(2 ** i)
            if i == max_retries - 1:
                return {
                    "principais_falhas": ["Erro 429: API sobrecarregada."],
                    "acoes_curto_prazo": ["Tentar novamente mais tarde."],
                    "resumo_geral": "Não foi possível gerar o feedback.",
                    "vicios_linguagem": [],
                }
        except Exception as e:
            return {
                "principais_falhas": ["Erro na API."],
                "acoes_curto_prazo": ["Verificar chave da API."],
                "resumo_geral": str(e),
                "vicios_linguagem": [],
            }

    try:
        data = json.loads(resp.text)
        data.setdefault("principais_falhas", [])
        data.setdefault("acoes_curto_prazo", [])
        data.setdefault("resumo_geral", "Resumo indisponível.")
        data.setdefault("vicios_linguagem", [])
    except:
        data = {
            "principais_falhas": ["Erro ao processar JSON."],
            "acoes_curto_prazo": ["Tentar novamente."],
            "resumo_geral": resp.text.strip(),
            "vicios_linguagem": [],
        }

    return data