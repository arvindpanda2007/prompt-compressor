# prompt-compressor
This compressor can be used for compressing prompts while preserving their semantic meaning. This tool helps reduce token count for LLM prompts without losing important information.

## Features

- **Rule-based compression** — a YAML file (`rules.yaml`) defines regex rule groups (filler removal, greeting removal, modifier stripping, phrase collapsing, punctuation cleanup) that you can edit without touching code.
- **Entity & contraction preservation** — quoted text, technical terms, and contractions (`don't`, `I'll`, etc.) are protected from being mangled by compression rules.
- **Token-level stats** — reports original vs. compressed token counts (via `tiktoken`'s `cl100k_base` encoding) and a compression ratio.
- **Two commands** — `compress` for the compressed prompt itself, `analyze` for a stats-only breakdown of compression opportunities.

## Installation

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/arvindpanda2007/prompt-compressor.git
cd prompt-compressor
uv sync
```

The first run will also download the `en_core_web_sm` spaCy model and tiktoken's `cl100k_base` encoding file — this needs an internet connection and happens automatically the first time you run a command.

## Usage

```bash
# Compress a prompt (prints the compressed text)
uv run prompt-compressor compress "Hi there, I would like to know if you could please tell me the weather today"

# Compress with full stats (original/compressed tokens, ratio)
uv run prompt-compressor compress "your prompt here" --stats

# Analyze a prompt for compression opportunities (stats only, doesn't require --stats)
uv run prompt-compressor analyze "your prompt here"

# Use a different rules file
uv run prompt-compressor compress "your prompt here" --rules path/to/custom_rules.yaml

# Save results to a JSON file
uv run prompt-compressor compress "your prompt here" --output result.json
```

`rules.yaml` at the project root is used by default, so `--rules` only needs to be passed when you want a different rule set.

### Options

| Command | Flag | Description |
|---|---|---|
| `compress` | `--rules, -r` | Path to a rules YAML file (defaults to `rules.yaml`) |
| `compress` | `--output, -o` | Save results as JSON |
| `compress` | `--verbose, -v` | Show original and compressed text side by side |
| `compress` | `--stats, -s` | Show token counts and compression ratio |
| `analyze` | `--rules, -r` | Path to a rules YAML file (defaults to `rules.yaml`) |
| `analyze` | `--verbose, -v` | Show detailed analysis |

## Customizing compression rules

`rules.yaml` defines named rule groups, each with a list of regex `pattern` → `replacement` pairs:

```yaml
rule_groups:
  remove_greetings:
    enabled: true
    patterns:
      - pattern: "\\b(hi|hello|hey|greetings|good (morning|afternoon|evening))\\b"
        replacement: ""
```

Disable a group by setting `enabled: false`, or add your own patterns to tune what gets stripped or collapsed.

## Project structure

```
prompt_compressor/
├── cli.py              # Typer CLI (compress, analyze commands)
├── core/
│   ├── compressor.py   # PromptCompressor — rule application, spaCy-based compression
│   ├── analyzer.py     # ContentAnalyzer — pattern detection for compression opportunities
│   └── types.py        # ContentType enum
└── tests/
rules.yaml               # Default compression rule set
sample-prompts.txt        # Example prompts for testing/experimentation
```

## Running tests

```bash
uv run pytest prompt_compressor/tests
```