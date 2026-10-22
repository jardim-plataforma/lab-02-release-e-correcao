"""Executa testes reais e uma sonda de falha controlada do laboratório."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cenario', choices=['normal', 'falha', 'falha-python312'],
                        default=os.environ.get('LAB_CENARIO', 'normal'))
    args = parser.parse_args()
    if args.cenario not in ('normal', 'falha', 'falha-python312'):
        parser.error('LAB_CENARIO inválido')
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover',
                             '-s', 'tests', '-v'], cwd=ROOT)
    forced = args.cenario == 'falha' or (
        args.cenario == 'falha-python312' and sys.version_info[:2] == (3, 12))
    code = result.returncode or (1 if forced else 0)
    report = {'cenario': args.cenario, 'python': sys.version.split()[0],
              'testes_exit_code': result.returncode, 'falha_controlada': forced,
              'exit_code': code}
    destination = ROOT / 'outputs'
    destination.mkdir(exist_ok=True)
    (destination / 'validacao.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False), flush=True)
    if forced:
        print('SONDA: falha controlada de verificação obrigatória.', file=sys.stderr)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
