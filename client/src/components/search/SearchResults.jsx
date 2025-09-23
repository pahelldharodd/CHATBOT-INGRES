import { useI18n } from '../../i18n/I18nContext'

export default function SearchResults() {
	const { t } = useI18n()
	return (
		<div className="rounded-lg border border-white/10 bg-slate-900 overflow-x-auto">
			<table className="min-w-full text-sm text-slate-200">
				<thead className="bg-slate-800 text-slate-200">
					<tr>
						<th className="px-4 py-2 text-left">{t.search.columns.region}</th>
						<th className="px-4 py-2 text-left">{t.search.columns.year}</th>
						<th className="px-4 py-2 text-left">{t.search.columns.status}</th>
						<th className="px-4 py-2 text-left">{t.search.columns.extraction}</th>
					</tr>
				</thead>
				<tbody>
					<tr className="border-top border-white/10">
						<td className="px-4 py-2">Uttar Pradesh</td>
						<td className="px-4 py-2">2021</td>
						<td className="px-4 py-2">{t.status.critical}</td>
						<td className="px-4 py-2">--</td>
					</tr>
				</tbody>
			</table>
		</div>
	)
}
