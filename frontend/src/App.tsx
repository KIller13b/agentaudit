import { useState } from 'react'
import Header from './components/Header'
import ModeToggle from './components/ModeToggle'
import PRInput from './components/PRInput'
import ContractInput from './components/ContractInput'
import AuditDashboard from './components/AuditDashboard'
import LoadingSpinner from './components/LoadingSpinner'
import type { AuditReport } from './types'

export type Mode = 'pr' | 'contract'

const API_BASE = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || '')

export async function runPRAudit(prUrl: string): Promise<AuditReport> {
  const res = await fetch(`${API_BASE}/audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pr_url: prUrl }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Server error: ${res.status}`)
  }
  return res.json()
}

export async function runContractAudit(code: string, filename?: string): Promise<AuditReport> {
  const res = await fetch(`${API_BASE}/audit/contract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, filename }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Server error: ${res.status}`)
  }
  return res.json()
}

export default function App() {
  const [mode, setMode] = useState<Mode>('contract')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<AuditReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAudit = async (payload: string, filename?: string) => {
    setLoading(true)
    setReport(null)
    setError(null)
    try {
      const result = mode === 'pr'
        ? await runPRAudit(payload)
        : await runContractAudit(payload, filename)
      setReport(result)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Header />
      <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
        <ModeToggle mode={mode} onChange={setMode} />

        {mode === 'pr' ? (
          <PRInput onAudit={handleAudit} loading={loading} />
        ) : (
          <ContractInput onAudit={handleAudit} loading={loading} />
        )}

        {loading && <LoadingSpinner />}

        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-950/30 p-4 text-red-400 text-sm">
            ⚠ {error}
          </div>
        )}

        {report && !loading && <AuditDashboard report={report} />}
      </main>
    </div>
  )
}
