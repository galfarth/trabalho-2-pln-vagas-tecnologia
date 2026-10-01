# Dataset da entrega

Esta pasta recebe os arquivos gerados pela coleta documentada no Trabalho 2.

## Estrutura esperada

```text
dados/
├── raw/
│   └── vagas_*.jsonl ou vagas_raw_*.jsonl
└── processed/
    └── vagas_processadas_*.csv
```

A execução usada no relatório foi realizada em 15/09/2026 e apresentou:

- 600 registros brutos;
- 568 vagas únicas após deduplicação;
- 32 duplicidades removidas;
- 0 descrições vazias na base final.

Após inserir os arquivos, valide com:

```bash
python scripts/validar_dataset.py
```
