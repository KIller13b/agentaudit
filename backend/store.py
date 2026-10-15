import time
from collections import deque
from threading import Lock

_started_at = time.time()
_lock = Lock()
_history: deque = deque(maxlen=200)
_seq = 0

_counters = {
    "total": 0,
    "pr": 0,
    "contract": 0,
    "issues": 0,
    "score_sum": 0,
    "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
    "grade": {"A": 0, "B": 0, "C": 0, "D": 0},
    "agents": {"guard": 0, "speedster": 0, "fixer": 0, "solidity": 0},
}


def bump_agent(name: str) -> None:
    with _lock:
        if name in _counters["agents"]:
            _counters["agents"][name] += 1


def record_audit(mode: str, target: str, report, duration_ms: float, status: str) -> dict:
    global _seq
    severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in report.issues:
        if issue.severity in severity:
            severity[issue.severity] += 1

    with _lock:
        _seq += 1
        record = {
            "id": _seq,
            "timestamp": time.time(),
            "mode": mode,
            "target": target,
            "files": report.files_analyzed,
            "grade": report.grade,
            "score": report.score,
            "issues": len(report.issues),
            "severity": severity,
            "duration_ms": int(round(duration_ms)),
            "status": status,
        }
        _history.appendleft(record)
        _counters["total"] += 1
        _counters[mode] += 1
        _counters["issues"] += len(report.issues)
        _counters["score_sum"] += report.score
        for key, value in severity.items():
            _counters["severity"][key] += value
        if report.grade in _counters["grade"]:
            _counters["grade"][report.grade] += 1

    return record


def get_history(limit: int = 50) -> list[dict]:
    with _lock:
        return [dict(r) for r in list(_history)[:limit]]


def get_stats(live_mode: bool) -> dict:
    with _lock:
        total = _counters["total"]
        recent = list(_history)[:10]
        return {
            "started_at": _started_at,
            "uptime_seconds": int(time.time() - _started_at),
            "mode": "live" if live_mode else "mock",
            "total_audits": total,
            "pr_audits": _counters["pr"],
            "contract_audits": _counters["contract"],
            "total_issues": _counters["issues"],
            "avg_score": round(_counters["score_sum"] / total, 1) if total else 0,
            "recent_avg_score": round(sum(r["score"] for r in recent) / len(recent), 1) if recent else 0,
            "grade_distribution": dict(_counters["grade"]),
            "severity_totals": dict(_counters["severity"]),
            "agent_calls": dict(_counters["agents"]),
        }


def get_agents(live_mode: bool) -> dict:
    with _lock:
        calls = dict(_counters["agents"])
    return {
        "mode": "live" if live_mode else "mock",
        "model": "openai/gpt-oss-120b" if live_mode else "regex-fallback",
        "agents": [
            {"id": "guard", "name": "Guard Agent", "role": "Security vulnerability scanner", "calls": calls["guard"]},
            {"id": "speedster", "name": "Speedster Agent", "role": "Performance issue detector", "calls": calls["speedster"]},
            {"id": "fixer", "name": "Fixer Agent", "role": "Patch & report generator", "calls": calls["fixer"]},
            {"id": "solidity", "name": "Solidity Agent", "role": "Web3 / smart contract scanner", "calls": calls["solidity"]},
        ],
    }
