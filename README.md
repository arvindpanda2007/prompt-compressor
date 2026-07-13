# prompt-compressor

A rule-based prompt compressor for LLM inputs. It strips filler words, greetings, hedging language, and verbose phrasing from a prompt while preserving quoted text, technical terms, and contractions — then reports exactly how many tokens you saved.

Useful anywhere prompt length translates directly into cost or latency: chatbots forwarding raw user input to an LLM, agent pipelines that accumulate verbose instructions, or any place you want to cut token spend without touching meaning.

## Example

```bash
$ prompt-compressor compress "Hi there, I would like to know if you could please tell me the weather today" --stats
```

```
you could tell me weather today.

=== Compression Statistics ===
Original tokens: 17
Compressed tokens: 7
Tokens saved: 10
Compression ratio: 58.82%
```

A less filler-heavy prompt compresses less aggressively, since there's less to strip:

```bash
$ prompt-compressor compress "I am really interested in learning more about how to set up a Kafka producer in Python" --stats
```

```
I am interested in learning more about how set up Kafka producer in Python.

=== Compression Statistics ===
Original tokens: 17
Compressed tokens: 15
Tokens saved: 2
Compression ratio: 11.76%
```

Indirect-question phrasing collapses into a direct one:

```bash
$ prompt-compressor compress "Could you please help me understand, in a lot of detail, what the difference is between SQL and NoSQL databases?"
```

```
Could you help me understand in lot of detail what difference is between SQL and NoSQL databases?
```

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

### `compress` — get the compressed prompt

```bash
# Compress a prompt (prints just the compressed text)
uv run prompt-compressor compress "Hi there, I would like to know if you could please tell me the weather today"
# → you could tell me weather today.

# Compress with full stats (original/compressed tokens, ratio)
uv run prompt-compressor compress "your prompt here" --stats

# Show original + compressed side by side, plus stats
uv run prompt-compressor compress "your prompt here" --verbose

# Save results to a JSON file instead of / as well as printing
uv run prompt-compressor compress "your prompt here" --output result.json

# Use a different rules file
uv run prompt-compressor compress "your prompt here" --rules path/to/custom_rules.yaml
```

`--output result.json` writes:

```json
{
  "original": "your prompt here",
  "compressed": "your prompt here",
  "original_tokens": 3,
  "compressed_tokens": 3,
  "reduction": 0.0
}
```

### `analyze` — see compression opportunities without compressing

```bash
uv run prompt-compressor analyze "your prompt here"
uv run prompt-compressor analyze "your prompt here" --verbose   # includes original/compressed text too
```

### Options reference

| Command | Flag | Description |
|---|---|---|
| `compress` | `--rules, -r` | Path to a rules YAML file (defaults to `rules.yaml`) |
| `compress` | `--output, -o` | Save results as JSON |
| `compress` | `--verbose, -v` | Show original and compressed text side by side |
| `compress` | `--stats, -s` | Show token counts and compression ratio |
| `analyze` | `--rules, -r` | Path to a rules YAML file (defaults to `rules.yaml`) |
| `analyze` | `--verbose, -v` | Show detailed analysis |

`rules.yaml` at the project root is used by default, so `--rules` only needs to be passed when you want a different rule set.

## Customizing compression rules

`rules.yaml` defines named rule groups, each with a list of regex `pattern` → `replacement` pairs. Groups shipped by default include `remove_fillers`, `remove_greetings`, `strip_modifiers`, and `collapse_phrases` (e.g. collapsing `"in order to"` → `"to"`, `"utilize"` → `"use"`, or `"could you explain/tell me about/describe"` → `"explain"`).

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
main.py                       # Entry point (delegates to the Typer CLI)
prompt_compressor/
├── cli.py                    # Typer CLI — compress, analyze commands
├── core/
│   ├── compressor.py         # PromptCompressor — rule application, token counting
│   ├── analyzer.py           # ContentAnalyzer — pattern detection for compression opportunities
│   └── types.py              # ContentType enum (text/question/code/command/unknown)
└── tests/
rules.yaml                    # Default compression rule set
sample_prompts.txt            # Example prompts for testing/experimentation
```

## Running tests

```bash
uv run pytest prompt_compressor/tests
```

## Notes

- Token counts are computed with OpenAI's `cl100k_base` tokenizer via `tiktoken`, so figures reflect GPT-family tokenization specifically — a different model's tokenizer may report slightly different counts.
- Compression is regex-based and rule-driven, not a learned model — it's fast and fully deterministic, but only as good as the rules in `rules.yaml`. Prompts that are already terse will see little to no reduction, by design.
