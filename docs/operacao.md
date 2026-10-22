# Operação: interpretar, executar e verificar

## Vocabulário usado na demanda

- **Workflow:** arquivo YAML que define os eventos e os trabalhos automatizados.
- **Job:** conjunto de etapas executado em um runner. Jobs diferentes não compartilham automaticamente a mesma pasta de trabalho.
- **Step:** uma ação ou comando dentro de um job.
- **Código de saída:** resultado do processo; zero indica sucesso, e um valor diferente indica falha.
- **Matriz:** execução do mesmo job com combinações de parâmetros, como versões de Python.
- **Artefato:** arquivo guardado por uma execução do Actions. Ele pode ser um relatório ou um pacote de entrega.
- **Tag:** referência Git que identifica um commit. Neste projeto, não deve ser movida depois de publicada.
- **GitHub Release:** página associada a uma tag, com notas e anexos. Criá-la não implanta o serviço.

## Cenários de validação

Execute na raiz do projeto:

```sh
python tools/validate.py --cenario normal
python tools/validate.py --cenario falha
python tools/validate.py --cenario falha-python312
```

Cada comando executa primeiro os testes da aplicação. Depois, avalia a sonda. Uma falha real dos testes continua sendo uma falha em qualquer cenário.

| Cenário | Python 3.11 | Python 3.12 |
|---|---|---|
| normal | Código 0 se os testes passarem | Código 0 se os testes passarem |
| falha | Código 1 | Código 1 |
| falha-python312 | Código 0 se os testes passarem | Código 1 |

Confira imediatamente `$LASTEXITCODE` no PowerShell ou `$?` no Bash. O relatório é reescrito em `outputs/validacao.json` a cada execução local; ele não deve ser versionado. Um cenário forçado não altera os arquivos do serviço.

## Reproduzir no GitHub Actions

Abra **Actions → Validação do catálogo → Run workflow**. Selecione a branch que deseja investigar e o cenário. Verifique o nome da branch e o SHA mostrado na execução antes de interpretar o resultado. O botão exige que o workflow exista na branch padrão, embora a execução possa usar outra branch.

No começo, use `normal`. Durante o incidente, use `falha` na linha 1.0. Na release, use também `falha-python312`, depois de configurar a matriz. Em pushes e PRs, o cenário padrão é normal; as falhas controladas são executadas manualmente.

A mesma alteração pode provocar uma execução por push e outra por PR. Isso é esperado pela configuração inicial. Não confunda o resultado de uma referência com o de outra. Em execuções de PR, o GitHub pode testar um merge temporário; registre a revisão efetivamente usada.

Depois da correção, uma execução manual com falha provocada deve ficar reprovada. O sucesso do exercício está em obter a reprovação correta e impedir a entrega. Não altere a sonda para tornar tudo verde.

## Ferramentas prontas de empacotamento

O empacotador lê `config/package.json`, seleciona os arquivos de runtime e gera `dist/catalogo-VERSAO.zip`. Pode ser explorado localmente antes da integração na pipeline:

```sh
python tools/package.py
```

Sem `--release`, o ZIP é uma prévia local e não possui manifesto. O verificador de entrega deve rejeitá-lo. Isso não é outro incidente: faltam metadados por opção explícita do comando.

Para gerar um pacote identificado, use o SHA completo da revisão limpa que está sendo empacotada. Não use um SHA inventado ou de outro checkout. `git status --short` deve estar vazio após registrar suas mudanças; `dist/` e `outputs/` são ignorados.

PowerShell:

```powershell
$labCommit = (git rev-parse HEAD).Trim()
$labVersion = (Get-Content VERSION -Raw).Trim()
python tools/package.py --release --commit $labCommit
python tools/check_package.py "dist/catalogo-$labVersion.zip" --expected-version $labVersion --expected-commit $labCommit
```

Bash:

```sh
lab_commit=$(git rev-parse HEAD)
lab_version=$(cat VERSION)
python tools/package.py --release --commit "$lab_commit"
python tools/check_package.py "dist/catalogo-$lab_version.zip" --expected-version "$lab_version" --expected-commit "$lab_commit"
```

No runner, use o commit do checkout; `GITHUB_SHA` corresponde à revisão do evento quando o checkout padrão é mantido. Se mudar o ref de checkout, obtenha o SHA desse checkout. Para candidatos, use `VERSION` como `1.1.0-rc.1`; para a publicação final, `1.1.0`.

O empacotador apenas registra o SHA recebido. Ele não prova que o conteúdo corresponde a esse commit. A disciplina de checkout limpo, a execução identificada e a verificação da referência são partes obrigatórias da entrega. Não é assinatura de software.

## O que integrar na 1.1

A ferramenta está pronta; você deve escrever o YAML que coordena:

1. Validações em Python 3.11 e 3.12.
2. Um job separado de empacotamento, dependente do sucesso das validações.
3. Checkout e Python no próprio job de empacotamento.
4. Geração identificada e verificação do ZIP.
5. Upload do ZIP validado como artefato, com falha explícita se o arquivo esperado não existir.

A configuração de dependência entre jobs faz parte do exercício. Consulte `jobs.<job_id>.needs` na documentação. A verificação e a disponibilidade do artefato também precisam influenciar o resultado final; uma geração que falha não pode produzir uma entrega bem-sucedida.

Consulte a documentação de `actions/upload-artifact` para upload. Artefatos de jobs separados exigem transferência explícita se houver consumo entre runners; arquivos não aparecem automaticamente no outro job. Não são necessárias permissões de escrita no repositório para a validação inicial. A publicação de Releases será manual neste laboratório.

## Conferir o artefato baixado

Na execução correspondente à tag final, baixe o artefato. O download do Actions pode ser um ZIP contendo o ZIP `catalogo-1.1.0.zip`. Extraia o contêiner externo e valide o ZIP interno, sem recompilar ou remontar o conteúdo.

Obtenha o commit real da tag com `git rev-list -n 1 v1.1.0`. Use esse valor em `--expected-commit` e `1.1.0` em `--expected-version`. Passe o caminho do arquivo baixado a `tools/check_package.py`, em vez do caminho em `dist/`.

O verificador executa o runtime numa pasta temporária sem o código do checkout no caminho de importação. Também rejeita arquivos fora da lista de entrega e metadados divergentes. Um teste negativo útil é informar uma versão esperada incorreta: a ferramenta deve rejeitar o pacote.

## Publicação e recuperação

Associe as notas da corretiva à tag `v1.0.1`. Na 1.1, anexe à Release o mesmo ZIP baixado e verificado da execução da tag. As notas devem explicar o que mudou, como foi validado e como recuperar a automação.

Artefatos do Actions possuem retenção; um link de execução não é armazenamento permanente do pacote. Por isso, a entrega final inclui o anexo na Release. Nenhuma dessas operações instala o serviço em produção.

A recuperação deve preservar a correção do gate. Compare o comportamento recuperado com `v1.0.1`, não apenas com o código inicial. Não substitua tags publicadas. Caso a referência de recuperação não tenha job de pacote, isso deve ser uma limitação declarada, não um arquivo vazio apresentado como entrega.
