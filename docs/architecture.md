# Architectuur

Deze repo is bewust Markdown-first.

## Lagen

1. `docs/` — brongebonden Nederlandse gids over het koopproces.
2. `prompts/` — copy-pastebare agentinstructies.
3. `examples/` — synthetische cases voor veilig testen.
4. `scripts/check.py` — lokale validatie op structuur, bronsecties en privacy.

## Ontwerpkeuzes

- Geen live woningcases of persoonlijke bieddossiers.
- Geen database/runtime nodig.
- Nederlandse terminologie blijft leidend.
- Bronnen staan per document, zodat agenten context met herkomst kunnen laden.
