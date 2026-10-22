"""Ferramenta pronta: produz um ZIP operacional a partir de uma lista permitida."""
import argparse
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', action='store_true', help='Inclui release.json')
    parser.add_argument('--commit', help='SHA completo dos arquivos empacotados')
    args = parser.parse_args()
    if args.release and not re.fullmatch(r'[0-9a-f]{40}', args.commit or ''):
        parser.error('--release exige --commit com SHA completo de 40 caracteres')
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-rc\.\d+)?', version):
        parser.error('VERSION deve usar X.Y.Z ou X.Y.Z-rc.N')
    config = json.loads((ROOT / 'config/package.json').read_text(encoding='utf-8'))
    files = set()
    for entry in config['include']:
        source = ROOT / entry
        if not source.exists() or not source.resolve().is_relative_to(ROOT):
            parser.error(f'Entrada ausente ou fora do projeto: {entry}')
        for path in (source.rglob('*') if source.is_dir() else [source]):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
                    parser.error(f'Entrada não regular: {path}')
                files.add(path)
    output = ROOT / 'dist' / f'catalogo-{version}.zip'
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT).as_posix())
        if args.release:
            archive.writestr('release.json', json.dumps(
                {'version': version, 'commit': args.commit}, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
