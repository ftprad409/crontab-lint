# crontab-lint

A CLI tool that validates and explains crontab expressions with conflict detection.

## Installation

```bash
pip install crontab-lint
```

## Usage

Validate a crontab expression:

```bash
crontab-lint "*/5 * * * *"
```

**Output:**
```
✔ Valid expression
  → Runs every 5 minutes

No conflicts detected.
```

Validate and check for conflicts in a full crontab file:

```bash
crontab-lint --file /etc/cron.d/myjobs
```

**Options:**

| Flag | Description |
|------|-------------|
| `--file` | Path to a crontab file |
| `--explain` | Print a human-readable explanation |
| `--strict` | Treat warnings as errors |
| `--json` | Output results as JSON |

### Example with `--explain`

```bash
crontab-lint --explain "0 9 * * 1-5"
```

```
✔ Valid expression
  → Runs at 09:00 AM, Monday through Friday
```

### Example with `--json`

```bash
crontab-lint --json "*/15 * * * *"
```

```json
{
  "valid": true,
  "expression": "*/15 * * * *",
  "explanation": "Runs every 15 minutes",
  "conflicts": []
}
```

## Why crontab-lint?

- Catches syntax errors before deployment
- Detects overlapping or conflicting job schedules
- Human-readable explanations for complex expressions
- CI/CD friendly with non-zero exit codes on failure

## License

This project is licensed under the [MIT License](LICENSE).
