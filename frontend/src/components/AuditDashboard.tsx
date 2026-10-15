import type { AuditReport, Issue } from '../types'

interface Props {
  report: AuditReport
}

const SEVERITY_CONFIG = {
  critical: { label: 'CRITICAL', bg: 'bg-red-950/50', border: 'border-red-500/40', text: 'text-red-400', badge: 'bg-red-500/20 text-red-400 border-red-500/30' },
  high:     { label: 'HIGH',     bg: 'bg-orange-950/50', border: 'border-orange-500/40', text: 'text-orange-400', badge: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  medium:   { label: 'MEDIUM',   bg: 'bg-yellow-950/40', border: 'border-yellow-500/40', text: 'text-yellow-400', badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  low:      { label: 'LOW',      bg: 'bg-gray-900',       border: 'border-gray-700',      text: 'text-gray-400',  badge: 'bg-gray-500/20 text-gray-400 border-gray-600' },
}

const GRADE_CONFIG = {
  A: { color: 'text-green-400', ring: 'ring-green-500/40', bg: 'bg-green-950/30', label: 'Secure' },
  B: { color: 'text-yellow-400', ring: 'ring-yellow-500/40', bg: 'bg-yellow-950/30', label: 'Minor Issues' },
  C: { color: 'text-orange-400', ring: 'ring-orange-500/40', bg: 'bg-orange-950/30', label: 'Moderate Risk' },
  D: { color: 'text-red-400', ring: 'ring-red-500/40', bg: 'bg-red-950/30', label: 'High Risk' },
}

function IssueCard({ issue }: { issue: Issue }) {
  const cfg = SEVERITY_CONFIG[issue.severity] ?? SEVERITY_CONFIG.low
  return (
    <div className={`rounded-lg border ${cfg.border} ${cfg.bg} p-4 space-y-3`}>
      <div className="flex flex-wrap items-center gap-2">
        <span className={`text-xs font-bold border rounded-full px-2 py-0.5 ${cfg.badge}`}>
          {cfg.label}
        </span>
        <span className="text-xs border border-gray-700 text-gray-400 rounded-full px-2 py-0.5">
          {issue.category}
        </span>
        <span className="text-xs text-gray-600 ml-auto">
          {issue.file} · L{issue.line_start}–{issue.line_end}
        </span>
      </div>
      <p className={`text-sm ${cfg.text}`}>{issue.description}</p>

      {issue.original_code && (
        <div className="space-y-1">
          <div className="text-xs text-gray-500 font-medium">Vulnerable code:</div>
          <pre className="bg-gray-950 border border-gray-800 rounded-md px-3 py-2 text-xs text-red-300 overflow-x-auto whitespace-pre-wrap">
            {issue.original_code}
          </pre>
        </div>
      )}

      {issue.fixed_code && (
        <div className="space-y-1">
          <div className="text-xs text-green-500 font-medium">✓ Suggested fix:</div>
          <pre className="bg-gray-950 border border-green-800/40 rounded-md px-3 py-2 text-xs text-green-300 overflow-x-auto whitespace-pre-wrap">
            {issue.fixed_code}
          </pre>
        </div>
      )}
    </div>
  )
}

function SeverityCount({ label, count, className }: { label: string; count: number; className: string }) {
  return (
    <div className={`flex flex-col items-center rounded-lg p-3 border ${className}`}>
      <span className="text-2xl font-bold">{count}</span>
      <span className="text-xs text-gray-500 mt-0.5">{label}</span>
    </div>
  )
}

export default function AuditDashboard({ report }: Props) {
  const grade = report.grade as keyof typeof GRADE_CONFIG
  const gcfg = GRADE_CONFIG[grade] ?? GRADE_CONFIG.A

  const counts = {
    critical: report.issues.filter(i => i.severity === 'critical').length,
    high:     report.issues.filter(i => i.severity === 'high').length,
    medium:   report.issues.filter(i => i.severity === 'medium').length,
    low:      report.issues.filter(i => i.severity === 'low').length,
  }

  const grouped = {
    critical: report.issues.filter(i => i.severity === 'critical'),
    high:     report.issues.filter(i => i.severity === 'high'),
    medium:   report.issues.filter(i => i.severity === 'medium'),
    low:      report.issues.filter(i => i.severity === 'low'),
  }

  const orderedIssues: Issue[] = [
    ...grouped.critical,
    ...grouped.high,
    ...grouped.medium,
    ...grouped.low,
  ]

  return (
    <div className="space-y-5">
      {/* Score bar */}
      <div className={`rounded-xl border ${gcfg.ring.replace('ring', 'border')} ${gcfg.bg} p-6`}>
        <div className="flex flex-col sm:flex-row sm:items-center gap-5">
          {/* Grade circle */}
          <div className={`flex-shrink-0 w-20 h-20 rounded-full ring-4 ${gcfg.ring} ${gcfg.bg} flex flex-col items-center justify-center`}>
            <span className={`text-3xl font-black ${gcfg.color}`}>{report.grade}</span>
            <span className="text-xs text-gray-500">{gcfg.label}</span>
          </div>
          <div className="flex-1 space-y-2">
            <div className="text-sm text-gray-400">{report.summary}</div>
            {/* Score bar */}
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-gray-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    report.score >= 90 ? 'bg-green-500' :
                    report.score >= 75 ? 'bg-yellow-500' :
                    report.score >= 50 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${report.score}%` }}
                />
              </div>
              <span className="text-sm font-bold text-gray-300">{report.score}/100</span>
            </div>
          </div>
        </div>

        {/* Counts */}
        <div className="grid grid-cols-4 gap-2 mt-5">
          <SeverityCount label="Critical" count={counts.critical} className="border-red-800/40 text-red-400" />
          <SeverityCount label="High"     count={counts.high}     className="border-orange-800/40 text-orange-400" />
          <SeverityCount label="Medium"   count={counts.medium}   className="border-yellow-800/40 text-yellow-400" />
          <SeverityCount label="Low"      count={counts.low}      className="border-gray-700 text-gray-400" />
        </div>
      </div>

      {/* Issues list */}
      {orderedIssues.length === 0 ? (
        <div className="rounded-xl border border-green-800/40 bg-green-950/20 p-6 text-center text-green-400 text-sm">
          ✓ No issues found — code looks clean!
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-xs text-gray-500 font-medium uppercase tracking-widest">
            Issues · sorted by severity
          </div>
          {orderedIssues.map((issue, idx) => (
            <IssueCard key={idx} issue={issue} />
          ))}
        </div>
      )}
    </div>
  )
}
