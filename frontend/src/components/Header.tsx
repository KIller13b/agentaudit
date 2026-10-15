export default function Header() {
  return (
    <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-20">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🛡️</span>
          <span className="text-xl font-bold text-white tracking-tight">AgentAudit</span>
        </div>
        <span className="text-xs bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded-full px-2 py-0.5 ml-1">
          AI-powered
        </span>
        <div className="ml-auto flex items-center gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse inline-block"></span>
            3 Agents Active
          </span>
          <span>·</span>
          <span>Powered by Groq + Qwen/Llama</span>
        </div>
      </div>
    </header>
  )
}
