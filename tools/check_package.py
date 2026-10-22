"""Verifica metadados e executa o pacote numa pasta temporária sem o checkout."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

PROBE = r'''
import json, sys, threading
from urllib.request import urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
sys.path.insert(0, sys.argv[1])
from backend.server import Handler
server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = 'http://127.0.0.1:' + str(server.server_port)
try:
    with urlopen(base + '/health', timeout=5) as r:
        health = json.load(r)
        assert health['status'] == 'ok'
        assert health['version'] == sys.argv[2]
    for version, fields in [('v1', 3), ('v2', 5)]:
        with urlopen(base + '/api/' + version + '/recursos/svc-001', timeout=5) as r:
            assert len(json.load(r)) == fields
        try:
            urlopen(base + '/api/' + version + '/recursos/ausente', timeout=5)
        except HTTPError as error:
            assert error.code == 404
            assert json.load(error)['erro']['codigo'] == 'RECURSO_INEXISTENTE'
        else:
            raise AssertionError('Recurso ausente não retornou 404')
    for path in ['/', '/app.js', '/style.css']:
        with urlopen(base + path, timeout=5) as r:
            assert r.read()
    print('PACOTE EXECUTÁVEL: saúde, contratos, ausência e assets conferidos.')
finally:
    server.shutdown()
    server.server_close()
    thread.join()
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--expected-version', required=True)
    parser.add_argument('--expected-commit', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.expected_commit):
        parser.error('expected-commit precisa ser um SHA completo')
    with tempfile.TemporaryDirectory(prefix='lab02-pacote-') as directory:
        with zipfile.ZipFile(args.archive) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Entradas duplicadas no ZIP')
            for name in names:
                path = PurePosixPath(name)
                if (path.is_absolute() or '..' in path.parts or '\\' in name
                    or ':' in name or not path.parts):
                    raise ValueError('Caminho inválido no ZIP')
                if path.parts[0] not in ('backend', 'frontend', 'VERSION', 'EXECUTAR.md', 'release.json'):
                    raise ValueError(f'Arquivo fora do contrato de entrega: {name}')
                if '__pycache__' in path.parts or name.endswith('.pyc'):
                    raise ValueError('Cache de desenvolvimento no pacote')
            metadata = json.loads(archive.read('release.json'))
            if metadata.get('version') != args.expected_version:
                raise ValueError('Versão divergente no manifesto')
            if metadata.get('commit') != args.expected_commit:
                raise ValueError('Commit divergente no manifesto')
            if archive.read('VERSION').decode().strip() != args.expected_version:
                raise ValueError('VERSION divergente')
            archive.extractall(directory)
        subprocess.run([sys.executable, '-I', '-c', PROBE, directory,
                        args.expected_version], cwd=directory, check=True, timeout=20)
    print('ACEITO: metadados e execução isolada do pacote.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, zipfile.BadZipFile,
            subprocess.SubprocessError) as error:
        print(f'PACOTE REJEITADO: {error}', file=sys.stderr)
        raise SystemExit(1)
