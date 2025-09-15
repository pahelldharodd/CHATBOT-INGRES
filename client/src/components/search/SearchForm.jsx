import { useI18n } from '../../i18n/I18nContext'

export default function SearchForm() {
	const { t } = useI18n()
	return (
		<form className="rounded-lg border border-white/10 bg-slate-900 p-4 grid gap-4">
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				<select className="border border-white/10 bg-slate-800 text-slate-100 rounded px-3 py-2">
					<option>{t.search.region}</option>
					<option>Uttar Pradesh</option>
					<option>Maharashtra</option>
				</select>
				<select className="border border-white/10 bg-slate-800 text-slate-100 rounded px-3 py-2">
					<option>{t.search.year}</option>
					<option>2020</option>
					<option>2021</option>
				</select>
				<select className="border border-white/10 bg-slate-800 text-slate-100 rounded px-3 py-2">
					<option>{t.search.status}</option>
					<option>{t.status.safe}</option>
					<option>{t.status.critical}</option>
					<option>{t.status.overExploited}</option>
				</select>
			</div>
			<button type="submit" className="self-start rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-500">{t.search.searchBtn}</button>
		</form>
	)
}
