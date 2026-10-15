import type { Mode } from '../App'

interface Props {
  mode: Mode
  onChange: (m: Mode) => void
}

export default function ModeToggle({ mode, onChange }: Props) {
  return (
    <div className="flex gap-2 p-1 bg-gray-900 border border-gray-800 rounded-xl w-fit">
      <button
        onClick={() => onChange('contract')}
        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
          mode === 'contract'
            ? 'bg-violet-600 text-white shadow'
            : 'text-gray-400 hover:text-gray-200'
        }`}
      >
        ⬡ Smart Contract
      </button>
      <button
        onClick={() => onChange('pr')}
        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
          mode === 'pr'
            ? 'bg-blue-600 text-white shadow'
            : 'text-gray-400 hover:text-gray-200'
        }`}
      >
        ⎇ GitHub PR
      </button>
    </div>
  )
}
