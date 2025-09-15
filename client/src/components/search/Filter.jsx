import { useI18n } from '../../i18n/I18nContext'

export default function Filter() {
	const { t } = useI18n()
	return (
		<div className="rounded-lg border border-white/10 bg-slate-900 p-4 flex flex-wrap gap-3 text-slate-100">
			<span className="text-sm text-slate-300">{t.common.filters}</span>
			<button className="rounded border border-white/10 bg-slate-800 px-3 py-1 text-sm hover:bg-slate-700">{t.status.safe}</button>
			<button className="rounded border border-white/10 bg-slate-800 px-3 py-1 text-sm hover:bg-slate-700">{t.status.critical}</button>
			<button className="rounded border border-white/10 bg-slate-800 px-3 py-1 text-sm hover:bg-slate-700">{t.status.overExploited}</button>
		</div>
	)
}
