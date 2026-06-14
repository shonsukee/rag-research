# Database-Augmented RAG for Automated Repair of REST API Misuses

This repository contains an experimental pipeline for repairing deprecated REST API usage with LLMs and retrieval-augmented generation (RAG).

The current datasets cover Fitbit and SwitchBot API migrations. The pipeline stores API specifications in Pinecone, retrieves relevant specification contexts for each input program, and asks an OpenAI model to rewrite deprecated API usage to the latest API specification.

## Repository Layout

```text
.
├── dataset/          # Input programs and API specification URL lists
├── lib/
│   ├── apr/          # APR command entry point
│   ├── prompt/       # Prompt templates used by each method
│   └── store/        # API specification extraction and Pinecone storage
├── results/          # Generated repair outputs
├── Makefile          # Convenience commands
└── Dockerfile        # Reproducible Python runtime
```

## Supported Datasets

| Provider | Types |
| --- | --- |
| `fitbit` | `commits`, `issues`, `pull-requests` |
| `switchbot` | `commits`, `pull-requests` |

Each input file is stored under:

```text
dataset/{provider}/{type}/{id}.{extension}
```

API specification URLs are stored in:

```text
dataset/{provider}/url/latest.txt
dataset/{provider}/url/deprecated.txt
```

## Prompt Methods

Prompt templates are in `lib/prompt/`. Use the file name without `.md` as `prompt-name`.

| Method | Reference Information |
| --- | --- |
| `0_BL` | Baseline; latest spec links only |
| `1_D` | Deprecated spec |
| `2_L` | Latest spec |
| `3_DLm` | Deprecated and latest specs merged into one context |
| `4_DL` | Deprecated and latest specs as separate contexts |
| `5_Ds` | Deprecated spec split into natural language and code |
| `6_Ls` | Latest spec split into natural language and code |
| `7_DLs` | Deprecated spec plus latest split contexts |
| `8_DsL` | Deprecated split contexts plus latest spec |
| `9_DsLs` | Deprecated and latest specs split into natural language and code |
| `10_DcLc` | Deprecated and latest code snippets only |
| `11_DtLt` | Deprecated and latest natural-language text only |

See `lib/prompt/README.md` for the full prompt-template convention.

## Requirements

The pipeline needs:

- Python 3.12, or Docker
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- Pinecone indexes matching the prompt contexts you plan to use

Optional:

- `GITHUB_TOKEN`, only for scripts under `github/`

Create a local `.env` file if you run the Python commands directly:

```env
OPENAI_API_KEY=...
PINECONE_API_KEY=...
```

## Build

```bash
docker build -t rag .
```

## Store API Specifications

The store command reads URLs from `dataset/{provider}/url/{latest|deprecated}.txt`, extracts specification text, and stores it in Pinecone.

```bash
docker run --rm -v "$(pwd):/app" rag \
  make store name=<provider> version=<latest|deprecated> method=<all|separate> index-name=<pinecone-index>
```

`method=all` stores each specification page as a normal document in the provided index.

```bash
docker run --rm -v "$(pwd):/app" rag \
  make store name=fitbit version=latest method=all index-name=latest

docker run --rm -v "$(pwd):/app" rag \
  make store name=fitbit version=deprecated method=all index-name=deprecated
```

`method=separate` splits specification pages into natural-language text and code snippets. It stores them in indexes named from the version:

- `latest-natural-language`
- `latest-code`
- `deprecated-natural-language`
- `deprecated-code`

```bash
docker run --rm -v "$(pwd):/app" rag \
  make store name=switchbot version=latest method=separate index-name=latest

docker run --rm -v "$(pwd):/app" rag \
  make store name=switchbot version=deprecated method=separate index-name=deprecated
```

For `3_DLm`, store both latest and deprecated specs into the same `context` index:

```bash
docker run --rm -v "$(pwd):/app" rag \
  make store name=switchbot version=latest method=all index-name=context

docker run --rm -v "$(pwd):/app" rag \
  make store name=switchbot version=deprecated method=all index-name=context
```

## Run API Misuse Repair

```bash
docker run --rm -v "$(pwd):/app" rag \
  make apr name=<provider> types=<type> out=<output-dir> prompt-name=<method>
```

Examples:

```bash
docker run --rm -v "$(pwd):/app" rag \
  make apr name=fitbit types=commits out=./results prompt-name=2_L

docker run --rm -v "$(pwd):/app" rag \
  make apr name=switchbot types=pull-requests out=./results prompt-name=9_DsLs
```

Each input file is processed five times. Outputs are written to:

```text
{output-dir}/{prompt-name}/{provider}/{type}/{id}/{1..5}.md
```

Each output file contains:

- `# LLM Response`: generated repaired code
- `# User Query`: the full prompt sent to the model

## Existing Results

Generated outputs are already stored under `results/`. See `results/README.md` for the result directory structure and context-count summary.

## Notes

- Retrieval uses `similarity_top_k=60` and `SimilarityPostprocessor(similarity_cutoff=0.0)` in `lib/baseQuery.py`.
- The APR step reranks retrieved contexts with `LLMRerank(top_n=60)`.
- The generation model is currently configured as `o4-mini`.
- The embedding model is currently configured as `text-embedding-3-large`.
