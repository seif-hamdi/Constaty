# Constaty Insurance Crew

One sequential CrewAI crew processes the accident statement:

1. The multimodal intake agent creates strict JSON from the user's statement and photo.
2. The Pydantic `output_json` schema rejects missing, incorrectly typed, or extra fields.
3. The guardrail retries when `follow_up_questions` contains more than two entries.
4. `human_input: true` pauses for human review before the intake task completes.
5. The Risk Detector Agent classifies the accident under the FTUSA 25-case barème and validates the case with BaremeTesterTool.
6. The reviewed result continues to final reporting.

All roles, prompts, model selection, multimodal flags, expected outputs, human review settings, retry settings, and output files are in YAML. Python contains only the crew wiring, Pydantic schema, and guardrail function.

## Setup

Add your Gemini key to `.env`:

```env
GEMINI_API_KEY=your_key
```

Install and run:

```bash
uv sync
uv run crewai run
```

Gemini 2.5 Flash accepts image input. Enter a local image path or a public image URL when prompted.

## Main files

```text
src/constaty_insurance/
├── main.py
├── crew.py
├── models.py
├── guardrails.py
├── tools/
│   └── bareme_tester_tool.py
└── config/
    ├── agents.yaml
    └── tasks.yaml
```

Gemini is active in `agents.yaml`. The OpenRouter model is kept there as a comment beside each agent.

## FTUSA barème tool

`BaremeTesterTool` contains the 25-case FTUSA responsibility barème dated 1 June 1999. It uses an in-memory rule dictionary only; no Neo4j or database is used. Cases 24 and 25 are represented pairwise for deterministic X/Y validation.

## Risk indicator limit

The risk analysis output is schema-enforced to contain exactly three risk indicators. The final report must copy those same three indicators without adding more.
