from pydantic import BaseModel
from typing import Optional


class Issue(BaseModel):
    severity: str
    line_start: int
    line_end: int
    category: str
    description: str
    original_code: str
    fixed_code: Optional[str] = None
    file: str


class AuditReport(BaseModel):
    grade: str
    score: int
    summary: str
    issues: list[Issue]
    files_analyzed: int


class AuditRequest(BaseModel):
    pr_url: str
