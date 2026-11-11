"""
Arquivo de entrada principal (compatibilidade).
Para entender o código com mais facilidade, veja tambem: cena_besouro_drone.py
"""
from cena_besouro_drone import *  # noqa: F401,F403

if __name__ == "__main__":
    import cena_besouro_drone as cena
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int)
    parser.add_argument("--screenshot")
    parser.add_argument("--compat-display", action="store_true",
                        help="Exibe o quadro via janela SDL por software.")
    args = parser.parse_args()
    app = cena.Battlefield(title="Campo de batalha | Besouro mecanico e drone",
                           compat_display=args.compat_display)
    app.run(args.frames, args.screenshot)
