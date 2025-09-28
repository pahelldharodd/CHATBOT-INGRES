import { useI18n } from '../../i18n/I18nContext'

export default function DataSummary() {
		const { t } = useI18n()
		const title = (t && t.dashboard && t.dashboard.summaryTitle) ? t.dashboard.summaryTitle : 'Data Summary'
		const desc = (t && t.dashboard && t.dashboard.summaryDesc) ? t.dashboard.summaryDesc : 'Summary of recent updates and metrics.'
		return (
			<div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 hover:bg-slate-800/60 hover:border-cyan-400/40 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25 group">
				<h3 className="font-semibold mb-3 text-slate-100 group-hover:text-cyan-300 transition-colors duration-300">{title}</h3>
				<p className="text-sm text-slate-300 group-hover:text-slate-200 transition-colors duration-300 leading-relaxed">{desc}</p>
			</div>
		)
}
