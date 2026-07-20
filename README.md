# Constaty Insurance Crew

Constaty is a sequential **CrewAI** workflow for processing motor-accident declarations in Tunisia. It converts a user’s written statement and accident photo into structured claim data, pauses for human review, classifies responsibility using the **FTUSA 25-case barème**, and produces a final reviewed report.

The project is designed so that operational behavior remains configurable in YAML, while Python is limited to the crew wiring, validation schemas, guardrails, and the FTUSA validation tool.
Developed By: Seifeddine Hamdi / Nadhem Benhadjali

## Project presentation

The business presentation is available here:

**[Open the Constaty presentation in Canva](https://canva.link/dyo2nzsvzy68sm7)**

The presentation explains Constaty from an insurance-business perspective:

- the problem of incomplete, scattered, and difficult-to-review motor-claim evidence;
- the guided client journey for submitting text, voice, photos, videos, and documents;
- the insurance-agent review flow, including damage analysis and risk indicators;
- the role of human validation before any final decision;
- expected pilot outcomes such as faster first review, better submission completeness, and fewer follow-up requests;
- a recommended pilot with one insurer, three to five agencies, and material-damage claims over eight to twelve weeks;
- feasibility in Tunisia, including alignment with digital accident-declaration initiatives such as E-Constat;
- the project’s strengths, weaknesses, opportunities, threats, and possible business value.

The figures in the presentation are **pilot targets and business scenarios, not guaranteed results**. The core positioning is that Constaty supports insurance agents rather than replacing them: the system prepares and analyzes the claim file, while the insurer keeps control of the final decision.

## How the crew works

The crew runs sequentially.

1. **Multimodal intake**  
   The intake agent receives the user’s accident statement and an accident image. It converts the evidence into strict structured JSON.

2. **Schema validation**  
   A Pydantic `output_json` model validates the response. Missing fields, incorrect types, and unexpected extra fields are rejected.

3. **Guardrail validation**  
   A guardrail checks `follow_up_questions`. The task is retried when more than two follow-up questions are returned.

4. **Human review**  
   The intake task uses `human_input: true`, so execution pauses before completion and allows a reviewer to confirm or correct the extracted accident data.

5. **Risk and responsibility classification**  
   The Risk Detector Agent classifies the accident according to the FTUSA 25-case responsibility barème.

6. **Deterministic barème validation**  
   `BaremeTesterTool` checks the selected case against an in-memory rule dictionary. Cases 24 and 25 are represented as pairwise X/Y rules to keep validation deterministic.

7. **Final reporting**  
   The human-reviewed intake result and the validated responsibility analysis continue to the final report.

## Key guarantees

- Strict Pydantic validation for the intake output.
- No silent acceptance of missing, mistyped, or extra JSON fields.
- No more than two follow-up questions.
- Mandatory human review before the intake task completes.
- Responsibility classification validated against the FTUSA barème tool.
- Exactly three risk indicators in the risk-analysis output.
- The final report must copy the same three indicators without adding or replacing any.

## Technology

- [CrewAI](https://www.crewai.com/)
- Gemini 2.5 Flash for multimodal text-and-image input
- Pydantic for schema enforcement
- YAML for agents, tasks, prompts, models, retry settings, review settings, expected outputs, and output-file configuration
- Python for orchestration, schemas, guardrails, and the FTUSA test tool

## Setup

### 1. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the crew

```bash
uv run crewai run
```

Gemini 2.5 Flash accepts image input. When prompted, provide either:

- a local image path; or
- a publicly accessible image URL.

## Example interactive run

<p align="center">
  <img src="assets/constaty-cli-run.png" alt="Constaty CrewAI command-line run showing accident statement input, image URL input, agent startup, and the human review prompt" width="900">
</p>

The terminal example shows the full intake entry point:

1. `crewai run` starts the project.
2. The user enters an accident statement.
3. The user supplies a local image path or public image URL.
4. The **Multimodal Accident Intake Specialist** begins the structured-intake task.
5. Because the task uses `human_input: true`, CrewAI pauses and displays the draft result for reviewer confirmation before the workflow continues.

This review step is intentional: the Risk Detector Agent and final report receive the confirmed intake result rather than an unchecked model response.

## Project structure

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

## File responsibilities

### `main.py`

Application entry point. It collects the accident statement and image reference, then starts the CrewAI workflow.

### `crew.py`

Contains the crew wiring, agent/task loading, execution order, and tool registration.

### `models.py`

Defines the Pydantic output schemas used to enforce strict JSON structure and the exact risk-indicator count.

### `guardrails.py`

Contains the guardrail function that rejects intake output when `follow_up_questions` contains more than two items.

### `tools/bareme_tester_tool.py`

Implements `BaremeTesterTool`, an in-memory validator for the FTUSA 25-case responsibility barème dated 1 June 1999. It does not require Neo4j or another database.

### `config/agents.yaml`

Defines agent roles, goals, backstories, prompts, model selection, multimodal settings, and related runtime configuration.

Gemini is active in this file. The alternative OpenRouter model is preserved as a comment beside each agent.

### `config/tasks.yaml`

Defines task descriptions, expected outputs, output files, human-review settings, retry behavior, task dependencies, and schema-related configuration.

## Configuration philosophy

Constaty follows a configuration-first design:

- **YAML** controls agent behavior and operational settings.
- **Python** contains only reusable program logic.

This separation makes prompts, models, review behavior, retries, and output destinations easier to update without rewriting the orchestration code.

## FTUSA barème validation

`BaremeTesterTool` stores the 25 FTUSA cases in memory and validates the Risk Detector Agent’s result.

The tool is intended to:

- confirm that the selected case exists;
- verify that the accident configuration matches the case rules;
- keep responsibility classification deterministic;
- provide a testable layer between model reasoning and the final report.

Cases 24 and 25 use pairwise X/Y representations because the result depends on the relative position and behavior of both vehicles.

## Human-in-the-loop behavior

Human validation is a required workflow step, not an optional post-processing check.

When the intake task reaches its review point:

1. CrewAI pauses execution.
2. The reviewer inspects the structured accident data.
3. The reviewer confirms or corrects the result.
4. The reviewed result is passed to the Risk Detector Agent.
5. Final reporting uses the reviewed data rather than the original unconfirmed extraction.

This keeps the insurer or reviewer in control of the claim interpretation.

## Risk-indicator rule

The risk-analysis schema must contain exactly three indicators.

The final report must:

- reproduce those same three indicators;
- preserve their meaning;
- avoid adding a fourth indicator;
- avoid replacing them with newly generated indicators.

This rule keeps the analysis and final report consistent and prevents the reporting agent from expanding the risk assessment beyond the validated schema.

## Example input

```text
Statement:
I was driving straight through the intersection when another vehicle entered from my right and hit the front passenger side of my car.

Image:
Pipeline.png
```

## Expected workflow result

A successful run should produce:

- validated structured accident data;
- zero to two follow-up questions;
- a human-reviewed intake record;
- an FTUSA case classification;
- a deterministic barème validation result;
- exactly three risk indicators;
- a final claim-support report.

The exact filenames and output destinations are defined in `config/tasks.yaml`.

## Business objective

Constaty aims to improve the quality of the first claim file received by an insurer. A more complete initial declaration can reduce repeated information requests, speed up review, improve traceability, and help agents focus their attention on complex or higher-risk claims.

The platform does not make the final insurance decision. It prepares a clearer, more consistent, and review-ready file for the insurance professional.

## Disclaimer

This project is a claim-support and decision-assistance prototype. It does not replace an insurance expert, legal assessment, official accident report, or insurer decision. FTUSA barème results and risk indicators must remain subject to human validation and the insurer’s internal rules.
