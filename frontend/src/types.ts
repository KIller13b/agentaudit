export interface Issue {
  severity: 'critical' | 'high' | 'medium' | 'low'
  line_start: number
  line_end: number
  category: string
  description: string
  original_code: string
  fixed_code: string | null
  file: string
}

export interface AuditReport {
  grade: 'A' | 'B' | 'C' | 'D'
  score: number
  summary: string
  issues: Issue[]
  files_analyzed: number
}
