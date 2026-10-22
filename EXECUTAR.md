# Executar o catálogo

Requisitos: Python 3.11 ou 3.12. Não há dependências de terceiros.

Na pasta que contém `backend/`, `frontend/` e `VERSION`:

```sh
python -m backend.server
```

Abra http://127.0.0.1:8080. Para outra porta, use `python -m backend.server --port 8081`.
No Windows, `py -3.11` pode substituir `python`.

O serviço escuta somente em localhost. Use Ctrl+C para encerrar.
Os dados são fictícios e somente de leitura. Não há banco externo nem migrações.

Rotas: `/health`, `/api/v1/recursos/svc-001`, `/api/v2/recursos/svc-001`.
Um identificador ausente deve retornar 404 nas duas versões.
`VERSION` identifica a entrega deste laboratório, não a versão do contrato da API.
Quando presente, `release.json` informa a versão e o commit declarados pelo empacotamento.
Não é uma assinatura nem prova criptográfica de origem.
