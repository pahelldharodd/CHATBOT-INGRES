import SearchForm from '../components/search/SearchForm'
import SearchResults from '../components/search/SearchResults'
import Filter from '../components/search/Filter'
import { useEffect, useState } from 'react'
import Papa from 'papaparse'

export default function SearchPage() {
	const [rows, setRows] = useState([])
	const [loading, setLoading] = useState(true)
	const [errors, setErrors] = useState([])

		// filter state (region + district)
		const [region, setRegion] = useState('')
		const [regionOptions, setRegionOptions] = useState([])
		const [district, setDistrict] = useState('')
		const [year, setYear] = useState('')
		const [status, setStatus] = useState('')

		const [districtOptions, setDistrictOptions] = useState([])
		const [yearOptions, setYearOptions] = useState([])
			const [showFresh, setShowFresh] = useState(true)
			const [showSaline, setShowSaline] = useState(true)

		useEffect(() => {
		let cancelled = false
			const stateForDistrict = {}

		async function loadAll() {
			setLoading(true)
			const start = 2012
			const end = 2024
			const perYearAggregates = {}
			const stateDistricts = {}
			const missing = []

			for (let y = start; y <= end; y++) {
				const next = (y + 1).toString().slice(-2)
				const range = `${y}-${next}`
				const path = `/header_flat_csv/INGRES_${range}.csv`
				try {
					await new Promise((resolve) => {
						Papa.parse(path, {
							download: true,
							header: true,
							skipEmptyLines: true,
							complete: (res) => {
								const data = Array.isArray(res.data) ? res.data : []
								if (!data.length) {
									missing.push(path)
									resolve()
									return
								}

								data.forEach(r => {
									const state = (r.STATE || r.STATE_NAME || r.State || r.state || '').trim()
									const districtName = (r.DISTRICT || r.DISTRICT_NAME || r.District || r.district || '').trim()
									if (!state) return

									const primary = districtName || state
									const key = `${y}||${primary}`
									if (!perYearAggregates[key]) perYearAggregates[key] = { state, district: districtName || null, primary, year: y, gweSum: 0, aerSum: 0, count: 0, freshSum: 0, salineSum: 0 }

									const gweRaw = r['GWE_Tot'] || r['GWE_Tot '] || r['GWE_Tot\uFEFF'] || r['GWE_Tot']
									const gwe = gweRaw != null && gweRaw !== '' ? parseFloat(String(gweRaw).replace(/,/g, '')) : NaN
														if (!Number.isNaN(gwe)) {
															perYearAggregates[key].gweSum += gwe
														}

														const aerRaw = r['AER_Tot'] || r['AER_Tot '] || r['AER_Tot\uFEFF'] || r['AER_Tot']
														const aer = aerRaw != null && aerRaw !== '' ? parseFloat(String(aerRaw).replace(/,/g, '')) : NaN
														if (!Number.isNaN(aer)) {
															perYearAggregates[key].aerSum += aer
														}

									const ucaFr = parseFloat(String(r['UCA_FR'] || 0).replace(/,/g, '')) || 0
									const ucaSl = parseFloat(String(r['UCA_SL'] || 0).replace(/,/g, '')) || 0
									const cfaFr = parseFloat(String(r['CFA_FR'] || 0).replace(/,/g, '')) || 0
									const cfaSl = parseFloat(String(r['CFA_SL'] || 0).replace(/,/g, '')) || 0
									const tgahFr = parseFloat(String(r['TGAH_FR'] || 0).replace(/,/g, '')) || 0
									const tgahSl = parseFloat(String(r['TGAH_SL'] || 0).replace(/,/g, '')) || 0

									perYearAggregates[key].freshSum += ucaFr + cfaFr + tgahFr
									perYearAggregates[key].salineSum += ucaSl + cfaSl + tgahSl

									if (districtName) {
										if (!stateDistricts[state]) stateDistricts[state] = new Set()
										stateDistricts[state].add(districtName)
										stateForDistrict[districtName] = state
									} else {
										stateForDistrict[state] = state
									}
								})

								resolve()
							},
							error: () => { missing.push(path); resolve() }
						})
					})
				} catch {
					missing.push(path)
				}
				if (cancelled) break
			}

			if (cancelled) return

					const out = Object.values(perYearAggregates).map(s => {
						const gwePct = (s.aerSum > 0 && s.gweSum != null) ? (s.gweSum / s.aerSum) * 100 : null
						let statusCat = 'Unknown'
						if (gwePct != null) {
							if (gwePct >= 100) statusCat = 'Over-Exploited'
							else if (gwePct >= 90) statusCat = 'Critical'
							else if (gwePct >= 70) statusCat = 'Semi-Critical'
							else if (gwePct > 0) statusCat = 'Safe'
							else statusCat = 'Unknown'
						}
						return { state: s.state, district: s.district, primary: s.primary, year: s.year, status: statusCat, gwePct: gwePct, fresh: s.freshSum, saline: s.salineSum }
					})

			out.sort((a, b) => (a.primary || '').localeCompare(b.primary || '') || a.year - b.year)
			setRows(out)
			setErrors(missing)
			setLoading(false)

			const districtMap = {}
			Object.keys(stateDistricts).forEach(s => { districtMap[s] = Array.from(stateDistricts[s]).sort() })
			const uniqStates = Array.from(new Set(out.map(r => r.state))).sort()
			setRegionOptions(uniqStates)
			// initial district options empty until a region is chosen
			setDistrictOptions([])
			setYearOptions(Array.from(new Set(out.map(r => r.year))).sort((a,b)=>a-b).map(String))
			if (typeof window !== 'undefined') window.__stateDistricts = districtMap
			if (typeof window !== 'undefined') window.__stateForDistrict = stateForDistrict
		}

		loadAll()
		return () => { cancelled = true }
	}, [])

	const filteredRows = rows.filter(r => {
			if (region && r.state !== region) return false
			if (district && r.primary !== (district)) return false
		if (year && String(r.year) !== String(year)) return false
		if (status) {
			const map = { safe: 'Safe', semiCritical: 'Semi-Critical', critical: 'Critical', overExploited: 'Over-Exploited' }
			const desired = map[status] || ''
			if (desired && r.status !== desired) return false
		}
		return true
	})

		// when region changes, populate district options
		useEffect(() => {
			if (!region) {
				setDistrictOptions([])
				setDistrict('')
				return
			}
			const map = (typeof window !== 'undefined' && window.__stateDistricts) ? window.__stateDistricts : {}
			setDistrictOptions(map[region] || [])
		}, [region])

	return (
		<div className="mx-auto max-w-6xl px-4 py-8 grid gap-6">
							<SearchForm
						regionOptions={regionOptions}
						districtOptions={districtOptions}
						yearOptions={yearOptions}
						region={region}
						setRegion={setRegion}
						district={district}
						setDistrict={setDistrict}
						year={year}
						setYear={setYear}
						status={status}
						setStatus={setStatus}
								showFresh={showFresh}
								setShowFresh={setShowFresh}
								showSaline={showSaline}
								setShowSaline={setShowSaline}
					/>

			<Filter status={status} setStatus={setStatus} />

			<SearchResults rows={filteredRows} loading={loading} errors={errors} showFresh={showFresh} showSaline={showSaline} />
		</div>
	)
}
