import json
import os
from groq import Groq


SYSTEM_PROMPT = """You are a senior security engineer specializing in code review.
Analyze the provided code diff and identify ONLY security vulnerabilities.

Look for:
- Hardcoded secrets (API keys, passwords, tokens)
- SQL injection risks
- XSS vulnerabilities
- Unsafe deserialization
- Path traversal
- Command injection
- Insecure random number usage
- Missing input validation

Return a JSON array of findings. Each finding must have:
- severity: "critical" | "high" | "medium" | "low"
- line_start: line number (integer)
- line_end: line number (integer)
- description: clear explanation of the vulnerability
- original_code: the vulnerable code snippet

If no issues found, return an empty array [].
Respond with ONLY valid JSON, no markdown formatting."""


async def guard_agent(code: str, filename: str) -> list[dict]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _mock_security_findings(code, filename)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
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
            f["category"] = "security"
            f["file"] = filename
            f["fixed_code"] = None
        return findings
    except (json.JSONDecodeError, KeyError):
        return []


def _mock_security_findings(code: str, filename: str) -> list[dict]:
    findings = []
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if any(kw in stripped.lower() for kw in ["password", "api_key", "secret", "token"]):
            if "=" in stripped and not stripped.startswith("#"):
                findings.append(
                    {
                        "severity": "high",
                        "line_start": i,
                        "line_end": i,
                        "category": "security",
                        "description": f"Potential hardcoded secret detected in {filename}",
                        "original_code": stripped,
                        "file": filename,
                        "fixed_code": None,
                    }
                )
        if "exec(" in stripped or "eval(" in stripped:
            findings.append(
                {
                    "severity": "critical",
                    "line_start": i,
                    "line_end": i,
                    "category": "security",
                    "description": "Use of exec/eval can lead to arbitrary code execution",
                    "original_code": stripped,
                    "file": filename,
                    "fixed_code": None,
                }
            )
    return findings
