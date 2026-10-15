import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from main import audit_pr, audit_contract, ContractAuditRequest
from models import AuditRequest

SEVERITY_COLORS = {
    "critical": "\033[91m",
    "high": "\033[93m",
    "medium": "\033[36m",
    "low": "\033[90m",
}
RESET = "\033[0m"


def print_report(report):
    print(f"\n{'='*60}")
    print(f"  🛡️  AGENTAUDIT REPORT")
    print(f"{'='*60}")
    print(f"\n  Grade: {report.grade}  |  Score: {report.score}/100")
    print(f"  Files analyzed: {report.files_analyzed}")
    print(f"\n  {report.summary}")
    print(f"\n{'─'*60}")

    if not report.issues:
        print("\n  ✓ No issues found. Code looks clean!")
    else:
        for i, issue in enumerate(report.issues, 1):
            color = SEVERITY_COLORS.get(issue.severity, "")
            print(f"\n  [{color}{issue.severity.upper()}{RESET}] {issue.category} — {issue.file}")
            print(f"  Lines {issue.line_start}–{issue.line_end}")
            print(f"  {issue.description}")
            if issue.original_code:
                print(f"  Original: {issue.original_code[:80]}")
            if issue.fixed_code:
                print(f"  Fixed:    \033[92m{issue.fixed_code[:80]}\033[0m")

    print(f"\n{'='*60}\n")


async def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage:")
        print("  python audit.py <github-pr-url>        Audit a GitHub PR")
        print("  python audit.py <path-to-file.sol>      Audit a local Solidity contract or code file")
        sys.exit(1)

    target = sys.argv[1]

    # Check if target is a file or a GitHub PR
    if os.path.isfile(target):
        print(f"Auditing local file: {target}...")
        code = Path(target).read_text(encoding="utf-8")
        report = await audit_contract(ContractAuditRequest(code=code, filename=Path(target).name))
    elif "github.com" in target and "/pull/" in target:
        print(f"Auditing GitHub Pull Request: {target}...")
        report = await audit_pr(AuditRequest(pr_url=target))
    else:
        print("Error: Target must be a GitHub PR URL or a valid local file path.")
        sys.exit(1)

    print_report(report)

    output_path = Path("audit-report.json")
    output_path.write_text(report.model_dump_json(indent=2))
    print(f"Report saved to {output_path.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
