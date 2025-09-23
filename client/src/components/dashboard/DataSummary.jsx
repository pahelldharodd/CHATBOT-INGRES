import { useI18n } from '../../i18n/I18nContext'

export default function DataSummary() {
	const { t } = useI18n()
	return (
		<div className="rounded-lg border border-white/10 bg-slate-900 p-4 text-slate-100">
			<h3 className="font-medium mb-2">{t.dashboard.summaryTitle}</h3>
			<p className="text-sm text-slate-300">{t.dashboard.summaryDesc}</p>
		</div>
	)
}
