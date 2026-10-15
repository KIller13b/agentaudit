import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agents.guard import guard_agent
from agents.speedster import speedster_agent
from agents.fixer import fixer_agent
from agents.solidity import solidity_agent
from github import parse_pr_url, fetch_pr_files
from models import AuditRequest, AuditReport, Issue

load_dotenv()

app = FastAPI(title="AgentAudit", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEVERITY_SCORES = {"critical": 25, "high": 15, "medium": 8, "low": 3}


def compute_report(all_issues: list[Issue], files_count: int) -> AuditReport:
    total_penalty = sum(SEVERITY_SCORES.get(i.severity, 0) for i in all_issues)
    score = max(0, 100 - total_penalty)

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    summary = (
        f"Analyzed {files_count} file(s). Found {len(all_issues)} issue(s): "
        f"{sum(1 for i in all_issues if i.severity == 'critical')} critical, "
        f"{sum(1 for i in all_issues if i.severity == 'high')} high, "
        f"{sum(1 for i in all_issues if i.severity == 'medium')} medium, "
        f"{sum(1 for i in all_issues if i.severity == 'low')} low."
    )

    return AuditReport(
        grade=grade,
        score=score,
        summary=summary,
        issues=all_issues,
        files_analyzed=files_count,
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "live" if os.getenv("GROQ_API_KEY") else "mock"}


@app.post("/audit", response_model=AuditReport)
async def audit_pr(request: AuditRequest):
    """Audit a GitHub Pull Request URL."""
    parsed = parse_pr_url(request.pr_url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid GitHub PR URL. Expected: https://github.com/owner/repo/pull/123")

    owner, repo, pr_number = parsed
    files = await fetch_pr_files(owner, repo, pr_number, os.getenv("GITHUB_TOKEN"))

    if not files:
        return AuditReport(
            grade="A", score=100,
            summary="No auditable code changes found in this PR.",
            issues=[], files_analyzed=0,
        )

    all_issues: list[Issue] = []

    for file in files:
        code = file["patch"]
        filename = file["filename"]

        guard_results, speedster_results = await asyncio.gather(
            guard_agent(code, filename),
            speedster_agent(code, filename),
        )
        combined = guard_results + speedster_results

        if combined:
            fixes = await fixer_agent(code, combined, filename)
            fix_map = {(f["line_start"], f["line_end"]): f for f in fixes}

            for finding in combined:
                key = (finding["line_start"], finding["line_end"])
                fix = fix_map.get(key, {})
                all_issues.append(
                    Issue(
                        severity=finding["severity"],
                        line_start=finding["line_start"],
                        line_end=finding["line_end"],
                        category=finding["category"],
                        description=finding["description"],
                        original_code=finding["original_code"],
                        fixed_code=fix.get("fixed_code"),
                        file=filename,
                    )
                )

    return compute_report(all_issues, len(files))


class ContractAuditRequest(BaseModel):
    code: str
    filename: Optional[str] = "Contract.sol"


@app.post("/audit/contract", response_model=AuditReport)
async def audit_contract(request: ContractAuditRequest):
    """Audit a raw Solidity smart contract for Web3 vulnerabilities."""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Contract code cannot be empty.")

    filename = request.filename or "Contract.sol"

    # Run all three agents in parallel: Solidity-specific + general security + fixer
    sol_results, guard_results = await asyncio.gather(
        solidity_agent(request.code, filename),
        guard_agent(request.code, filename),
    )

    combined = sol_results + guard_results

    if combined:
        fixes = await fixer_agent(request.code, combined, filename)
        fix_map = {(f["line_start"], f["line_end"]): f for f in fixes}
    else:
        fix_map = {}

    all_issues: list[Issue] = []
    for finding in combined:
        key = (finding["line_start"], finding["line_end"])
        fix = fix_map.get(key, {})
        all_issues.append(
            Issue(
                severity=finding["severity"],
                line_start=finding["line_start"],
                line_end=finding["line_end"],
                category=finding.get("category", "security"),
                description=finding["description"],
                original_code=finding["original_code"],
                fixed_code=fix.get("fixed_code"),
                file=filename,
            )
        )

    return compute_report(all_issues, 1)
