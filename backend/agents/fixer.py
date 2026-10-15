import json
import os
from groq import Groq


SYSTEM_PROMPT = """You are a senior software engineer who writes clean, correct fixes for code issues.
Given a list of findings (each with description, original_code, severity, and category),
produce a fixed version of the code for each finding.

Return a JSON array of fixes. Each fix must have:
- line_start: matching the finding's line_start
- line_end: matching the finding's line_end
- fixed_code: the corrected code that resolves the issue
- explanation: brief description of what was changed

If a finding cannot be auto-fixed, set fixed_code to null.
Respond with ONLY valid JSON, no markdown formatting."""


async def fixer_agent(code: str, findings: list[dict], filename: str) -> list[dict]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _mock_fixes(findings)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"File: {filename}\n\nOriginal code:\n```\n{code}\n```\n\nFindings:\n{json.dumps(findings, indent=2)}",
            },
        ],
        temperature=0.2,
        max_tokens=4096,
    )

    try:
        fixes = json.loads(response.choices[0].message.content)
        return fixes
    except (json.JSONDecodeError, KeyError):
        return []


def _mock_fixes(findings: list[dict]) -> list[dict]:
    fixes = []
    for f in findings:
        original = f.get("original_code", "")
        fixed = None
        explanation = "No automated fix available"

        if f["category"] == "security":
            if "exec(" in original or "eval(" in original:
                fixed = original.replace("exec(", "safe_exec(").replace("eval(", "ast.literal_eval(")
                explanation = "Replaced unsafe exec/eval with safe alternatives"
            elif any(kw in original.lower() for kw in ["password", "api_key", "secret", "token"]):
                fixed = original + "  # TODO: Move to environment variable"
                explanation = "Flagged secret — manual rotation required"
        elif f["category"] == "performance":
            if "time.sleep(" in original:
                fixed = original.replace("time.sleep(", "await asyncio.sleep(")
                explanation = "Replaced blocking sleep with async alternative"

        fixes.append(
            {
                "line_start": f.get("line_start", 0),
                "line_end": f.get("line_end", 0),
                "fixed_code": fixed,
                "explanation": explanation,
            }
        )
    return fixes
