import { useState } from 'react'
import { SAMPLE_PR_URL } from '../samples'

interface Props {
  onAudit: (prUrl: string) => void
  loading: boolean
}

export default function PRInput({ onAudit, loading }: Props) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) onAudit(url.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5 space-y-3">
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
          <span>⎇</span>
          <span>Paste a public GitHub Pull Request URL</span>
        </div>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo/pull/123"
          className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 transition"
          required
        />
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white text-sm font-medium rounded-lg transition"
          >
            {loading ? 'Auditing…' : 'Run Audit'}
          </button>
          <button
            type="button"
            onClick={() => setUrl(SAMPLE_PR_URL)}
            className="px-4 py-2.5 border border-gray-700 hover:border-gray-500 text-gray-400 hover:text-gray-200 text-sm rounded-lg transition"
          >
            Try Sample PR
          </button>
        </div>
      </div>
    </form>
  )
}
