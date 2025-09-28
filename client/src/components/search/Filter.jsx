import { useI18n } from '../../i18n/I18nContext'

export default function Filter({ status, setStatus }) {
	const { t } = useI18n()
	const opts = [
		{ key: '', label: t.common.all || 'All' },
		{ key: 'safe', label: t.status.safe },
		{ key: 'semiCritical', label: t.status.semiCritical },
		{ key: 'critical', label: t.status.critical },
		{ key: 'overExploited', label: t.status.overExploited }
	]

	return (
		<div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 flex flex-wrap gap-4 text-slate-100 shadow-lg">
			<span className="text-sm text-slate-200 font-semibold">{t.common.filters}</span>
			{opts.map(o => (
				<button key={o.key} onClick={() => setStatus(o.key)} className={`rounded-xl border px-4 py-2 text-sm font-medium transition-all duration-300 ${status === o.key ? 'bg-cyan-600/80 border-cyan-400/50 text-white shadow-lg shadow-cyan-500/25' : 'bg-slate-800/60 border-slate-600/50 text-slate-200 hover:bg-slate-700/60 hover:border-cyan-500/30'}`}>{o.label}</button>
			))}
		</div>
	)
}
