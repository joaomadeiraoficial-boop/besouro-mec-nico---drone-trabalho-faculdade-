"""Atalho de execução (compatibilidade): roda a etapa01."""
from etapa01_main import *  # noqa: F401,F403

if __name__ == "__main__":
    import etapa01_main as entrada
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int)
    parser.add_argument("--screenshot")
    parser.add_argument("--compat-display", action="store_true",
                        help="Exibe o quadro via janela SDL por software.")
    args = parser.parse_args()
    app = entrada.Battlefield(title="Campo de batalha | Besouro mecanico e drone",
                              compat_display=args.compat_display)
    app.run(args.frames, args.screenshot)
