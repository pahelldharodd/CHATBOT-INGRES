import TimelineChart from '../components/visualization/TimelineChart'
import GroundwaterChart from '../components/visualization/GroundwaterChart'

export default function HistoricalDataPage() {
	return (
		<div className="mx-auto max-w-6xl px-4 py-8 grid gap-6">
			<TimelineChart />
			<GroundwaterChart />
		</div>
	)
}
