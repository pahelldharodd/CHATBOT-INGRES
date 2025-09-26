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
		<div className="rounded-lg border border-white/10 bg-slate-900 p-4 flex flex-wrap gap-3 text-slate-100">
			<span className="text-sm text-slate-300">{t.common.filters}</span>
			{opts.map(o => (
				<button key={o.key} onClick={() => setStatus(o.key)} className={`rounded border px-3 py-1 text-sm ${status === o.key ? 'bg-blue-600 border-blue-600' : 'bg-slate-800 border-white/10'} hover:bg-slate-700`}>{o.label}</button>
			))}
		</div>
	)
}
