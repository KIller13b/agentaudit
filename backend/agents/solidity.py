"""
solidity.py — Solidity / Smart Contract Security Agent
Detects Web3-specific vulnerabilities: reentrancy, access control, overflow, etc.
Falls back to regex-based rules when no GROQ_API_KEY is present.
"""

import json
import os
import re
from groq import Groq


SYSTEM_PROMPT = """You are an expert smart contract security auditor specializing in Solidity.
Analyze the provided Solidity code and identify ALL security vulnerabilities.

Focus on:
- Reentrancy (state update AFTER external call)
- Missing access control (public/external functions that should be onlyOwner)
- Integer overflow/underflow (without SafeMath or Solidity 0.8+)
- tx.origin authentication (use msg.sender instead)
- Unchecked return values from low-level calls (.call, .send, .transfer)
- Timestamp dependence (block.timestamp for randomness)
- Self-destruct misuse
- Delegatecall to untrusted contracts
- Uninitialized storage pointers
- Floating pragma (pragma solidity ^0.x.x instead of fixed)

Return a JSON array of findings. Each finding must have:
- severity: "critical" | "high" | "medium" | "low"
- line_start: line number (integer)
- line_end: line number (integer)
- category: one of ["reentrancy", "access_control", "overflow", "tx_origin",
  "unchecked_call", "timestamp", "self_destruct", "delegatecall", "other"]
- description: clear explanation of the vulnerability and why it is dangerous
- original_code: the vulnerable code snippet (max 120 chars)

If no issues found, return an empty array [].
Respond with ONLY valid JSON, no markdown formatting."""

# --- Regex-based mock patterns (used when no API key) ---
SOLIDITY_PATTERNS = [
    {
        "pattern": re.compile(
            r"\.call\{value:", re.IGNORECASE
        ),
        "severity": "critical",
        "category": "reentrancy",
        "description": (
            "External .call{value:} detected before state update — "
            "potential reentrancy attack (see The DAO hack, $60M lost)."
        ),
    },
    {
        "pattern": re.compile(r"tx\.origin", re.IGNORECASE),
        "severity": "high",
        "category": "tx_origin",
        "description": (
            "tx.origin used for authentication — vulnerable to phishing attacks. "
            "Use msg.sender instead."
        ),
    },
    {
        "pattern": re.compile(
            r"function\s+\w+\s*\([^)]*\)\s+(?:public|external)\s+(?!.*onlyOwner)(?!.*view)(?!.*pure).*\{",
            re.IGNORECASE,
        ),
        "severity": "high",
        "category": "access_control",
        "description": (
            "Public/external state-changing function without access control modifier. "
            "Consider adding onlyOwner or a role-based modifier."
        ),
    },
    {
        "pattern": re.compile(r"block\.timestamp\s*[%<>]", re.IGNORECASE),
        "severity": "medium",
        "category": "timestamp",
        "description": (
            "block.timestamp used in arithmetic comparison — miners can manipulate "
            "timestamps by ~15 seconds, breaking randomness or time-locked logic."
        ),
    },
    {
        "pattern": re.compile(r"selfdestruct\s*\(", re.IGNORECASE),
        "severity": "high",
        "category": "self_destruct",
        "description": (
            "selfdestruct() call detected — if not protected by onlyOwner, "
            "any attacker can destroy the contract and steal its ETH balance."
        ),
    },
    {
        "pattern": re.compile(r"delegatecall\s*\(", re.IGNORECASE),
        "severity": "critical",
        "category": "delegatecall",
        "description": (
            "delegatecall to an external address detected — if the target is "
            "untrusted or upgradeable, it can overwrite your contract's storage."
        ),
    },
    {
        "pattern": re.compile(r"pragma\s+solidity\s+\^", re.IGNORECASE),
        "severity": "low",
        "category": "other",
        "description": (
            "Floating pragma (^) detected — pin the Solidity version to a fixed "
            "release for deterministic builds and audit reproducibility."
        ),
    },
]


async def solidity_agent(code: str, filename: str) -> list[dict]:
    """Run the Solidity security agent. Uses Groq LLM if key present, else regex rules."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _mock_solidity_findings(code, filename)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"File: {filename}\n\n```solidity\n{code}\n```",
            },
        ],
        temperature=0.1,
        max_tokens=3000,
    )

    try:
        findings = json.loads(response.choices[0].message.content)
        for f in findings:
            f["file"] = filename
            f.setdefault("fixed_code", None)
        return findings
    except (json.JSONDecodeError, KeyError):
        return _mock_solidity_findings(code, filename)


def _mock_solidity_findings(code: str, filename: str) -> list[dict]:
    findings = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for rule in SOLIDITY_PATTERNS:
            if rule["pattern"].search(stripped):
                findings.append(
                    {
                        "severity": rule["severity"],
                        "line_start": i,
                        "line_end": i,
                        "category": rule["category"],
                        "description": rule["description"],
                        "original_code": stripped[:120],
                        "file": filename,
                        "fixed_code": None,
                    }
                )
    return findings
