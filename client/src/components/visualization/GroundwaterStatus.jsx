import { useI18n } from '../../i18n/I18nContext'

export default function GroundwaterStatus() {
	const { t } = useI18n()
	const stages = [
		{ label: t.status.safe, color: 'bg-emerald-500' },
		{ label: t.status.semiCritical, color: 'bg-amber-500' },
		{ label: t.status.critical, color: 'bg-orange-600' },
		{ label: t.status.overExploited, color: 'bg-red-600' },
	]
	return (
		<div className="rounded-lg border border-white/10 bg-slate-900 p-4 text-slate-100">
			<h3 className="font-medium mb-3">{t.viz.groundwaterStatus}</h3>
			<div className="flex flex-wrap gap-3">
				{stages.map(s => (
					<div key={s.label} className="flex items-center gap-2">
						<span className={`h-3 w-3 rounded ${s.color}`} />
						<span className="text-sm text-slate-200">{s.label}</span>
					</div>
				))}
			</div>
		</div>
	)
}
