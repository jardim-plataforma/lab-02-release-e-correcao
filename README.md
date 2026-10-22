# Lab 02 · Operar uma correção durante a preparação de uma release

Este projeto é um laboratório público de engenharia de plataforma. O serviço já está implementado; o trabalho é manter sua automação de validação e entrega. O cenário exige corrigir uma pipeline que mascara falhas enquanto outra versão da automação está em estabilização.

**Estado inicial:** versão 1.0.0, testes da aplicação funcionais e um defeito deliberado no workflow. Este workflow é material de investigação, não um padrão pronto para reutilizar em outros projetos. A solução do incidente e o workflow final da 1.1 não estão implementados.

[Enunciado completo](ENUNCIADO.md) · [Página no jardim](https://jardim-plataforma.github.io/jardim-plataforma/laboratorios/02-release-e-correcao) · [Operação e ferramentas](docs/operacao.md) · [Git Flow na prática](docs/fluxo.md)

## Responsabilidade de quem realiza a prática

Investigar a sinalização incorreta do CI, entregar a corretiva 1.0.1, preparar a 1.1 com duas versões de Python e um pacote rastreável, propagar a correção e ensaiar recuperação. O serviço serve como carga de trabalho; seus endpoints e contratos não precisam ser modificados.

## Executar e reconhecer a base

Requisitos: Git e Python 3.11 ou 3.12. A validação remota usa GitHub Actions. Não é necessário instalar bibliotecas Python.

Na raiz do projeto:

```sh
python tools/validate.py --cenario normal
python -m backend.server
```

Abra http://127.0.0.1:8080. Encerre com Ctrl+C. No Windows, use `py -3.11` no lugar de `python` se necessário. O verificador é independente do servidor manual: os testes iniciam suas próprias instâncias temporárias.

Para provocar a falha controlada:

```sh
python tools/validate.py --cenario falha
```

Este comando **deve retornar código 1**, mesmo com os testes da aplicação aprovados. A sonda representa uma verificação obrigatória reprovada; ela não simula um defeito real no catálogo. Compare o retorno local com a execução manual do workflow no GitHub. O relatório local fica em `outputs/validacao.json`.

## Onde trabalhar

| Caminho | Papel |
|---|---|
| `.github/workflows/validacao.yml` | Automação inicial a investigar e evoluir |
| `VERSION` | Versão da entrega do laboratório |
| `config/package.json` | Lista dos arquivos de runtime empacotados |
| `tools/validate.py` | Testes e sonda controlada; pronto para uso |
| `tools/package.py` | Empacotador pronto; a integração em CI é sua tarefa |
| `tools/check_package.py` | Verificação do pacote em pasta temporária |
| `backend/`, `frontend/`, `consumidores/`, `tests/` | Serviço estável e suas verificações |
| `EXECUTAR.md` | Instruções que acompanham o runtime |
| `docs/` | Contexto, contratos operacionais e percurso de trabalho |

`dist/` e `outputs/` são saídas locais ignoradas pelo Git. O repositório não contém um ZIP de distribuição pré-construído.

## Primeiro passo do estudo

Leia o enunciado, execute o cenário normal e identifique como o workflow chega ao comando de validação. A referência `v1.0.0`, quando registrada no histórico, preserva o ponto inicial. O roteiro de branches está em [docs/fluxo.md](docs/fluxo.md).

A 1.0 não publica artefatos pela pipeline. As ferramentas locais já permitem explorar o empacotamento, mas isso não significa que a integração da 1.1 esteja resolvida.

## Evidências e autoria

Use PRs para explicar mudanças, verificações e riscos. Em uma prática individual, identifique a revisão como própria; não registre uma aprovação independente que não ocorreu. Acrescente a resolução no jardim com os resultados realmente observados.

A origem do serviço está documentada em [docs/origem.md](docs/origem.md). Todos os dados são de demonstração.
