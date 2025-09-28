import { useI18n } from '../../i18n/I18nContext'

export default function SearchResults({ rows = [], loading = false, errors = [], showFresh = true, showSaline = true }) {
	const { t } = useI18n()
		const fmt = (v) => {
		  // generic number formatter (returns string)
		  if (v == null || Number.isNaN(v)) return '0'
		  return (Math.round(v * 100) / 100).toLocaleString()
		}

		const fmtPercent = (v) => {
			if (v == null || Number.isNaN(v)) return '0%'
			return `${(Math.round(v * 100) / 100).toLocaleString()}%`
		}

		const fmtNumber = (v) => fmt(v)

	const borderClassFor = (status) => {
		if (!status) return 'border-slate-700'
		switch (status) {
			case 'Safe': return 'border-green-500'
			case 'Semi-Critical': return 'border-amber-500'
			case 'Critical': return 'border-violet-500'
			case 'Over-Exploited': return 'border-red-600'
			default: return 'border-slate-700'
		}
	}

	const badgeClassFor = (status) => {
		if (!status) return 'bg-slate-600 text-white'
		switch (status) {
			case 'Safe': return 'bg-green-600 text-white'
			case 'Semi-Critical': return 'bg-amber-500 text-black'
			case 'Critical': return 'bg-violet-600 text-white'
			case 'Over-Exploited': return 'bg-red-600 text-white'
			default: return 'bg-slate-600 text-white'
		}
	}

	return (
		<div>
			{loading && (
				<div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10 mb-4">
					<div className="flex items-center gap-3">
						<div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
						<span className="text-sm text-slate-200">Loading state/year data (2012-2024)…</span>
					</div>
				</div>
			)}
			{!loading && errors.length > 0 && (
				<div className="bg-amber-900/20 backdrop-blur-sm rounded-xl p-3 border border-amber-500/20 mb-4">
					<div className="text-xs text-amber-300">Note: missing files for some years: {errors.join(', ')}</div>
				</div>
			)}

			<div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl shadow-lg overflow-hidden">
				<table className="min-w-full text-sm text-slate-200">
							<thead className="bg-slate-800/40 backdrop-blur-sm text-slate-200 border-b border-cyan-500/20">
								<tr>
									{/* show district column when rows include district */}
									{rows.some(r => r.district) && <th className="px-4 py-2 text-left">District</th>}
									<th className="px-4 py-2 text-left">Year</th>
									<th className="px-4 py-2 text-left">Status</th>
									<th className="px-4 py-2 text-right">GWE (%)</th>
									{showFresh && <th className="px-4 py-2 text-right">Fresh (ham)</th>}
									{showSaline && <th className="px-4 py-2 text-right">Saline (ham)</th>}
								</tr>
							</thead>
					<tbody>
										{rows.length === 0 && !loading && (() => {
											const hasDistrict = rows.some(r => r.district)
											const colCount = (hasDistrict ? 1 : 0) + 1 /*Year*/ + 1 /*Status*/ + 1 /*GWE*/ + (showFresh ? 1 : 0) + (showSaline ? 1 : 0)
											return (<tr><td className="px-4 py-2" colSpan={colCount}>No data available. Place `INGRES_YYYY-YY.csv` files under `public/header_flat_csv` for years 2012-2024.</td></tr>)
										})()}
									{rows.map((r, i) => {
										const borderClass = borderClassFor(r.status)
										const badgeClass = badgeClassFor(r.status)
										return (
											<tr key={`${r.primary || ''}__${r.district || ''}__${r.year}__${i}`} className={`border-t border-white/5 border-l-4 ${borderClass}`}>
												{r.district ? <td className="px-4 py-2">{r.district}</td> : <td className="px-4 py-2">0</td>}
												<td className="px-4 py-2">{r.year}</td>
																	<td className="px-4 py-2">
																		<span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${badgeClass}`} title={r.status}>{t.status[r.status === 'Safe' ? 'safe' : r.status === 'Semi-Critical' ? 'semiCritical' : r.status === 'Critical' ? 'critical' : r.status === 'Over-Exploited' ? 'overExploited' : 'safe'] || r.status}</span>
																		{r.status === 'Critical' && (
																			<span className="ml-2 inline-block text-violet-600" title="Critical — requires attention">
																				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="inline-block"><path d="M10.29 3.86L1.82 18a1.13 1.13 0 0 0 .95 1.66h18.46a1.13 1.13 0 0 0 .95-1.66L13.71 3.86a1.13 1.13 0 0 0-1.82 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
																			</span>
																		)}
																	</td>
													<td className="px-4 py-2 text-right">{fmtPercent(r.gwePct)}</td>
													{showFresh && <td className="px-4 py-2 text-right">{fmtNumber(r.fresh)}</td>}
													{showSaline && <td className="px-4 py-2 text-right">{fmtNumber(r.saline)}</td>}
											</tr>
										)
									})}
					</tbody>
				</table>
			</div>
		</div>
	)
}
