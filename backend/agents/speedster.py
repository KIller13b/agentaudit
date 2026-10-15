import json
import os
from groq import Groq


SYSTEM_PROMPT = """You are a senior performance engineer specializing in code optimization.
Analyze the provided code diff and identify ONLY performance issues.

Look for:
- N+1 query patterns
- Unnecessary nested loops
- Blocking I/O in async contexts
- Memory leaks (unbounded lists, missing cleanup)
- Missing pagination
- Redundant computations
- Unindexed database queries

Return a JSON array of findings. Each finding must have:
- severity: "critical" | "high" | "medium" | "low"
- line_start: line number (integer)
- line_end: line number (integer)
- description: clear explanation of the performance issue
- original_code: the problematic code snippet

If no issues found, return an empty array [].
Respond with ONLY valid JSON, no markdown formatting."""


async def speedster_agent(code: str, filename: str) -> list[dict]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _mock_performance_findings(code, filename)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"File: {filename}\n\n```diff\n{code}\n```"},
        ],
        temperature=0.1,
        max_tokens=2048,
    )

    try:
        findings = json.loads(response.choices[0].message.content)
        for f in findings:
            f["category"] = "performance"
            f["file"] = filename
            f["fixed_code"] = None
        return findings
    except (json.JSONDecodeError, KeyError):
        return []


def _mock_performance_findings(code: str, filename: str) -> list[dict]:
    findings = []
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "for " in stripped and any(
            next_line.strip().startswith("for ") for next_line in lines[i : i + 5]
        ):
            findings.append(
                {
                    "severity": "medium",
                    "line_start": i,
                    "line_end": i,
                    "category": "performance",
                    "description": "Nested loops detected — potential O(n²) complexity",
                    "original_code": stripped,
                    "file": filename,
                    "fixed_code": None,
                }
            )
        if "time.sleep(" in stripped or "requests.get(" in stripped:
            findings.append(
                {
                    "severity": "medium",
                    "line_start": i,
                    "line_end": i,
                    "category": "performance",
                    "description": "Blocking I/O call in what may be an async context",
                    "original_code": stripped,
                    "file": filename,
                    "fixed_code": None,
                }
            )
    return findings
