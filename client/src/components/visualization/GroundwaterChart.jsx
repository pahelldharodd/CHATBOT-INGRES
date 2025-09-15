import { useI18n } from '../../i18n/I18nContext'

export default function GroundwaterChart() {
	const { t } = useI18n()
	return (
		<div className="h-64 rounded-lg border border-white/10 bg-slate-900 grid place-items-center">
			<span className="text-slate-400 text-sm">{t.viz.chartPlaceholder}</span>
		</div>
	)
}
