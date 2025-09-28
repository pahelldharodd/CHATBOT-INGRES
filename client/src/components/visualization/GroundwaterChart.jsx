import { useI18n } from '../../i18n/I18nContext'

export default function GroundwaterChart() {
	const { t } = useI18n()
	return (
		<div className="h-80 md:h-96 lg:h-[450px] rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 grid place-items-center group">
			<span className="text-slate-400 text-sm group-hover:text-slate-300 transition-colors duration-300">{t.viz.chartPlaceholder}</span>
		</div>
	)
}
