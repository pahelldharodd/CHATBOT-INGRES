import { useI18n } from '../../i18n/I18nContext'

export default function DataSummary() {
		const { t } = useI18n()
		const title = (t && t.dashboard && t.dashboard.summaryTitle) ? t.dashboard.summaryTitle : 'Data Summary'
		const desc = (t && t.dashboard && t.dashboard.summaryDesc) ? t.dashboard.summaryDesc : 'Summary of recent updates and metrics.'
		return (
			<div className="rounded-lg border border-white/10 bg-slate-900 p-4 text-slate-100">
				<h3 className="font-medium mb-2">{title}</h3>
				<p className="text-sm text-slate-300">{desc}</p>
			</div>
		)
}
