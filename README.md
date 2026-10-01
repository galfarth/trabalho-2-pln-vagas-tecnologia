# Trabalho 2 — Processamento de Linguagem Natural

## Coleta e Pré-processamento de Vagas de Tecnologia

**Universidade Regional de Blumenau (FURB)**  
**Curso:** Bacharelado em Ciência da Computação  
**Disciplina:** Processamento de Linguagem Natural  
**Autores:** Gabriel Schroeder Alfarth e Davi Deschamps  
**Ano:** 2026

## Sobre o trabalho

Este repositório reúne o código, o notebook, a documentação e a estrutura de dados utilizados no **Trabalho 2 de Processamento de Linguagem Natural**.

O objetivo da etapa é coletar anúncios de vagas de tecnologia por meio da API da **Adzuna** e transformar o conteúdo textual em uma base estruturada e preparada para tarefas posteriores de PLN, preservando também o texto original para auditoria e reprocessamento.

A execução documentada no relatório foi realizada em **15 de setembro de 2026** e obteve:

| Indicador | Resultado |
|---|---:|
| Registros brutos | 600 |
| Vagas únicas | 568 |
| Duplicidades removidas | 32 (5,3%) |
| Descrições vazias | 0 |
| Base processada | 568 vagas (94,7%) |
| Período de publicação das vagas | 2 a 14 de setembro de 2026 |

## Consultas realizadas

Foram usadas seis expressões de busca:

1. `desenvolvedor`
2. `analista de dados`
3. `cientista de dados`
4. `devops`
5. `segurança da informação`
6. `suporte de tecnologia`

A configuração utilizada busca **2 páginas de 50 resultados para cada consulta**, totalizando até 600 registros brutos.

## Etapas de pré-processamento

O fluxo implementado contempla:

- coleta paginada na API da Adzuna;
- achatamento dos objetos retornados pela API;
- deduplicação por `id_vaga`;
- descarte de anúncios sem descrição;
- preservação do texto original;
- remoção de HTML, URLs, e-mails e espaços repetidos;
- conversão para minúsculas;
- normalização Unicode e remoção de acentos;
- tokenização com tratamento de termos técnicos;
- remoção de stopwords;
- stemming com RSLP/NLTK;
- lematização opcional com spaCy;
- salvamento da base bruta em JSONL;
- salvamento da base processada em CSV UTF-8.

A tokenização foi preparada para preservar tecnologias como `C++`, `C#`, `.NET` e `Node.js`.

## Estrutura do repositório

```text
trabalho-2-pln-vagas-tecnologia/
│
├── README.md
├── coleta_preprocessamento_vagas.py
├── requirements.txt
├── .env.example
├── .gitignore
├── POSTAGEM_MOODLE.md
├── GUIA_GITHUB.md
│
├── notebook/
│   └── Trabalho_2_PLN_Coleta_Vagas_Colab.ipynb
│
├── dados/
│   ├── README.md
│   ├── metadata_dataset.json
│   ├── dados_vagas.zip
│   ├── raw/
│   └── processed/
│
├── scripts/
│   └── validar_dataset.py
│
└── relatorio/
    └── Trabalho_2_PLN_Gabriel_Alfarth_Davi_Deschamps.docx
```

## Google Colab

O notebook original está disponível em:

https://colab.research.google.com/drive/1uxgahnamTBnbJMZKi3IfSY9bfIivRkfc

O mesmo notebook também está versionado na pasta `notebook/`.

## Instalação local

Recomenda-se Python 3.10 ou superior.

```bash
python -m venv .venv
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

No Windows CMD:

```cmd
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Para usar lematização com spaCy:

```bash
python -m spacy download pt_core_news_sm
```

## Credenciais da Adzuna

Crie gratuitamente as credenciais no portal da Adzuna Developer API.

As credenciais **não devem ser colocadas no código nem enviadas ao GitHub**.

No Linux/macOS:

```bash
export ADZUNA_APP_ID="seu_app_id"
export ADZUNA_APP_KEY="sua_app_key"
```

No Windows CMD:

```cmd
set ADZUNA_APP_ID=seu_app_id
set ADZUNA_APP_KEY=sua_app_key
```

O arquivo `.env.example` documenta apenas os nomes das variáveis e não contém chaves reais.

## Execução

Execução equivalente à configuração documentada no trabalho:

```bash
python coleta_preprocessamento_vagas.py --paginas 2 --resultados 50
```

Com lematização:

```bash
python coleta_preprocessamento_vagas.py --paginas 2 --resultados 50 --lematizar
```

Os arquivos são gravados em:

```text
dados/raw/
dados/processed/
```

## Dataset

A entrega utiliza dois níveis de dados:

- **`dados/dados_vagas.zip`**: pacote com o dataset original da execução entregue;
- **`dados/raw/`**: registros coletados da API em JSON Lines (também disponíveis dentro do ZIP);
- **`dados/processed/`**: base deduplicada e pré-processada em CSV UTF-8 (também disponível dentro do ZIP).

A coleta documentada no relatório gerou **600 registros brutos e 568 vagas únicas**.

> Importante: a API retorna resultados dependentes da data. Para reproduzir exatamente a entrega de 15/09/2026, mantenha no repositório os arquivos gerados naquela execução. Uma nova execução poderá retornar vagas e quantidades diferentes.

O script `scripts/validar_dataset.py` verifica automaticamente a presença e os principais indicadores do dataset inserido no repositório.

## Validação do dataset

Depois de colocar o JSONL e o CSV nas pastas correspondentes, execute:

```bash
python scripts/validar_dataset.py
```

Para a coleta original, o esperado é:

```text
Registros brutos: 600
Vagas processadas: 568
IDs únicos no CSV: 568
Descrições vazias no CSV: 0
```

## Principais campos

| Campo | Descrição |
|---|---|
| `id_vaga` | Identificador da vaga fornecido pela API ou hash de contingência |
| `consulta_origem` | Expressão de busca que recuperou o anúncio |
| `titulo` | Título original da vaga |
| `descricao` | Descrição textual original |
| `empresa` | Empresa informada pela fonte |
| `localizacao` | Localização retornada pela API |
| `categoria` | Categoria ocupacional |
| `salario_minimo` | Limite salarial mínimo quando disponível |
| `salario_maximo` | Limite salarial máximo quando disponível |
| `tipo_contrato` | Tipo de contrato quando disponível |
| `data_publicacao` | Data de publicação |
| `url` | URL de redirecionamento da vaga |
| `coletado_em_utc` | Momento da coleta |
| `texto_original` | Título + descrição antes do tratamento |
| `texto_sem_ruidos` | Texto após remoção de ruídos |
| `texto_normalizado` | Texto normalizado |
| `tokens` | Tokens identificados |
| `tokens_sem_stopwords` | Tokens após remoção de stopwords |
| `texto_processado` | Texto filtrado utilizado nas próximas etapas |
| `stems` | Radicais produzidos pelo stemming |
| `lemas` | Lemas produzidos opcionalmente pelo spaCy |

## Observações de reprodutibilidade

Os resultados podem variar porque as vagas disponíveis na Adzuna mudam ao longo do tempo. O repositório mantém a separação entre código, dados brutos e dados processados para facilitar auditoria e reprodução das etapas.

## Referências principais

- Adzuna Developer API — https://developer.adzuna.com/
- NLTK — https://www.nltk.org/
- pandas — https://pandas.pydata.org/docs/
- spaCy — https://spacy.io/models
- O*NET Resource Center — https://www.onetcenter.org/database.html