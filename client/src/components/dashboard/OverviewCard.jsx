export default function OverviewCard({ title, value, tone = 'gray' }) {
	const toneMap = {
		emerald: 'text-emerald-400',
		amber: 'text-amber-400',
		red: 'text-red-400',
		gray: 'text-slate-200',
	}
	return (
		<div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 hover:bg-slate-800/60 hover:border-cyan-400/40 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25 group">
			<p className="text-sm text-slate-300 group-hover:text-slate-200 transition-colors duration-300">{title}</p>
			<p className={`text-3xl font-bold ${toneMap[tone]} group-hover:text-glow transition-all duration-300`}>{value}</p>
		</div>
	)
}
