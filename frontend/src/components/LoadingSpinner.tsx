export default function LoadingSpinner() {
  const agents = [
    { icon: '🛡️', name: 'Guard Agent', desc: 'Scanning for vulnerabilities…' },
    { icon: '⚡', name: 'Speedster Agent', desc: 'Checking performance…' },
    { icon: '🛠️', name: 'Fixer Agent', desc: 'Preparing code patches…' },
  ]

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6 space-y-4">
      <div className="text-sm text-gray-400 font-medium">Running 3 AI agents in parallel…</div>
      <div className="space-y-3">
        {agents.map((a) => (
          <div key={a.name} className="flex items-center gap-3">
            <span className="text-xl">{a.icon}</span>
            <div className="flex-1">
              <div className="text-sm text-gray-300 font-medium">{a.name}</div>
              <div className="text-xs text-gray-500">{a.desc}</div>
            </div>
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-1.5 h-4 bg-violet-500 rounded-full animate-pulse"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
