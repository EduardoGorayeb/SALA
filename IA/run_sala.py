from sala.analyzer import SalaAnalyzer
import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("[SALA] Uso correto: python run_sala.py caminho_do_video tema tipo [contexto_opcional]", flush=True)
        sys.exit(1)

    video_path = Path(sys.argv[1]).resolve()
    tema = sys.argv[2]
    tipo = sys.argv[3]

    contexto = None
    if len(sys.argv) >= 5:
        contexto = sys.argv[4]

    analyzer = SalaAnalyzer()
    report = analyzer.process(
        video_path,
        tema,
        tipo,
        save_json=True,
        contexto_apresentacao=contexto
    )

    print("[SALA] Relatório gerado com sucesso", flush=True)
    print("[SALA] Arquivo:", f"SALA_{video_path.stem}_report.json", flush=True)