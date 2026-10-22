# Git Flow: duas frentes de entrega

O objetivo do fluxo é permitir uma correção pequena da linha publicada enquanto outra versão está em estabilização. O nome das branches não executa essa política sozinho; origem, destino, revisão e testes dão significado ao histórico.

## Referência inicial

O ponto inicial do laboratório é `main` com `VERSION` em 1.0.0. A tag `v1.0.0` deve apontar para esse estado. Se já existir, examine seu commit e não a sobrescreva. Ao repetir a prática, use uma cópia independente ou referências identificadas para a repetição; não destrua a resolução anterior.

## Percurso sugerido

Os comandos abaixo pressupõem uma principal atualizada e um diretório de trabalho limpo. Confira `git status` antes de trocar de branch. Nenhum comando de descarte é necessário.

1. Crie `develop` de `main`; em seguida, crie `feat/entrega-rastreavel` de `develop`.
2. Desenvolva a melhoria operacional e proponha um PR de `feat/entrega-rastreavel` para `develop`.
3. Depois de integrar, crie `release/1.1` de `develop`. A candidata ainda tem verificações pendentes.
4. Reproduza o incidente na linha publicada e crie `hotfix/validacao-obrigatoria` de `main`.
5. Proponha o hotfix para `main`. Valide normal e falha antes e depois da integração e registre `v1.0.1`.
6. Incorpore a correção à release ativa. Um PR de hotfix para release pode ser usado enquanto a branch existir. Se ela tiver sido apagada, use uma branch de integração criada da release e incorpore a referência corretiva verificada.
7. Estabilize, ajuste a versão final e proponha `release/1.1` para `main`.
8. Confira a principal integrada, marque `v1.1.0`, valide a execução da tag e publique o pacote verificado.
9. Proponha os ajustes de `release/1.1` para `develop`. Faça isso antes de excluir a branch de release.

Use merge commits nos PRs deste exercício para tornar os caminhos visíveis e preservar a ancestralidade entre as linhas. Squash e rebase não são proibidos em outros contextos, mas mudam a leitura do histórico e tornam a comparação desta prática menos direta.

## Criar branches sem antecipar a solução

```sh
git switch main
git pull --ff-only
git switch -c develop
git push -u origin develop
git switch -c feat/entrega-rastreavel
```

Depois do PR da melhoria integrado em develop:

```sh
git switch develop
git pull --ff-only
git switch -c release/1.1
git push -u origin release/1.1
```

Para a correção da linha publicada:

```sh
git switch main
git pull --ff-only
git switch -c hotfix/validacao-obrigatoria
```

Não execute os três blocos de uma vez: entre eles há implementação, revisão e validação. Se a branch já existir, examine seu histórico e use `git switch NOME`; não tente recriá-la nem sobrescrevê-la.

## Por que não juntar tudo em main imediatamente?

A corretiva precisa conter apenas a restauração da validação obrigatória. Se partir de develop ou integrar toda a release para resolver o incidente, você levará também a evolução ainda não liberada.

| Momento | main | release/1.1 |
|---|---|---|
| Antes do hotfix | Automação inicial | Matriz e entrega em estabilização |
| Depois da propagação | Correção, sem evolução | Correção mais evolução |
| Após a release final | Versão completa 1.1 | Linha encerrada após devolver ajustes |

`VERSION` pode conflitar: o hotfix usa 1.0.1, enquanto a release usa 1.1.0-rc.1 e depois 1.1.0. Resolva pelo propósito da linha, não escolhendo automaticamente um lado do conflito. Na release, preserve a versão futura e a correção do workflow.

Main não é um servidor; develop não é um ambiente de desenvolvimento; release não é uma instalação de homologação. Os nomes descrevem linhas de trabalho. Neste exercício não há deploy automatizado.

## Tags, notas e evidências

Crie uma tag somente depois de conferir o commit integrado correspondente. Para uma tag anotada, `git rev-parse v1.1.0` pode retornar o objeto da tag; use `git rev-list -n 1 v1.1.0` para obter o commit.

Registre nas notas a versão anterior, mudança, verificações, limitações e caminho de recuperação. Na corretiva, mostre a ausência da evolução. Na release, mostre a presença das duas mudanças e o funcionamento do pacote. Nunca declare que Actions passou apenas porque os testes locais passaram.

## Recuperação

Crie uma branch `recovery/...` a partir de uma referência identificada e ensaie nela. Se optar por reverter, examine o tipo de commit: merges possuem mais de um pai e exigem escolher conscientemente qual linha preservar. Não use `git reset --hard` com push forçado para restaurar a principal. Explique os efeitos da recuperação na geração de pacotes e na correção da validação.

## Comparação com os outros fluxos

GitHub Flow organiza propostas que voltam diretamente à principal após revisão. Trunk-Based enfatiza incrementos pequenos integrados frequentemente e pode usar PRs e branches curtas. Aqui há uma linha permanente develop e uma release em estabilização separada da linha publicada: essa separação intencional é o Git Flow praticado.
