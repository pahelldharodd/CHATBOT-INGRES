import OverviewCard from '../components/dashboard/OverviewCard'
import DataSummary from '../components/dashboard/DataSummary'
import GroundwaterMap from '../components/visualization/GroundwaterMap'
import { useI18n } from '../i18n/I18nContext'

export default function DashboardPage() {
	const { t } = useI18n()
	return (
		<div className="mx-auto max-w-6xl px-4 py-8 grid gap-6">
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				<OverviewCard title={t.dashboard.overview.safeRegions} value="--" tone="emerald" />
				<OverviewCard title={t.dashboard.overview.criticalRegions} value="--" tone="amber" />
				<OverviewCard title={t.dashboard.overview.overExploited} value="--" tone="red" />
			</div>
			<DataSummary />
			<GroundwaterMap />
		</div>
	)
}
