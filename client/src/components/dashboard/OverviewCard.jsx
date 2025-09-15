export default function OverviewCard({ title, value, tone = 'gray' }) {
	const toneMap = {
		emerald: 'text-emerald-400',
		amber: 'text-amber-400',
		red: 'text-red-400',
		gray: 'text-slate-200',
	}
	return (
		<div className={`rounded-lg border border-white/10 bg-slate-900 p-4`}>
			<p className="text-sm text-slate-300">{title}</p>
			<p className={`text-2xl font-semibold ${toneMap[tone]}`}>{value}</p>
		</div>
	)
}
