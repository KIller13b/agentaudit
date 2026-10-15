import { useState } from 'react'
import { SAMPLE_VULNERABLE_CONTRACT } from '../samples'

interface Props {
  onAudit: (code: string, filename: string) => void
  loading: boolean
}

export default function ContractInput({ onAudit, loading }: Props) {
  const [code, setCode] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (code.trim()) onAudit(code.trim(), 'Contract.sol')
  }

  const loadSample = () => setCode(SAMPLE_VULNERABLE_CONTRACT)

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>⬡</span>
            <span>Paste your Solidity smart contract code</span>
          </div>
          <button
            type="button"
            onClick={loadSample}
            className="text-xs border border-violet-500/40 text-violet-400 hover:text-violet-200 hover:border-violet-400 rounded-md px-3 py-1 transition"
          >
            Load Demo Contract
          </button>
        </div>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder={`// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n\ncontract YourContract {\n    ...\n}`}
          rows={14}
          spellCheck={false}
          className="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-violet-500 transition font-mono resize-y"
          required
        />
        <button
          type="submit"
          disabled={loading || !code.trim()}
          className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm font-medium rounded-lg transition"
        >
          {loading ? 'Auditing Contract…' : '🔍 Audit Contract'}
        </button>
      </div>
    </form>
  )
}
