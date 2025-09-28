import { useEffect, useMemo, useRef, useState, useCallback } from 'react'
import { MapContainer, TileLayer, GeoJSON, Tooltip as LTooltip } from 'react-leaflet'
import Papa from 'papaparse'
import 'leaflet/dist/leaflet.css'

export default function GroundwaterMap({ mapId = 'map1', stageData = [], ingresData = [] }) {
	const geoJsonRef = useRef(null)
	const [publicGeoJson, setPublicGeoJson] = useState(null)
	const [geoJsonError, setGeoJsonError] = useState(null)
	const [fullIngresData, setFullIngresData] = useState([])
	const [ingresLoading, setIngresLoading] = useState(false)

	// Reset data when mapId changes to ensure fresh load
	useEffect(() => {
		if (mapId !== 'map1') {
			setFullIngresData([])
		}
	}, [mapId])

	// Load specific CSV dataset for each map
	useEffect(() => {
		if (mapId !== 'map1' && fullIngresData.length === 0 && !ingresLoading) {
			setIngresLoading(true)
			
			// Define specific CSV files for each map
			const mapFiles = {
				'map2': 'RR_TOT_2024-2025.csv',      // Rainfall data
				'map3': 'AGR_TOT_2024-2025.csv',     // Annual Groundwater Recharge
				'map4': 'AER_TOT_2024-2025.csv'      // Annual Extractable Resource
			}
			
			const fileName = mapFiles[mapId]
			if (!fileName) {
				console.warn(`No file defined for ${mapId}`)
				setIngresLoading(false)
				return
			}
			
			const loadMapData = async () => {
				const csvPath = `/Dashboard_CSV/${fileName}`
				
				try {
					const response = await fetch(csvPath)
					if (response.ok) {
						const csvText = await response.text()
						
						Papa.parse(csvText, {
							header: true,
							skipEmptyLines: true,
							transformHeader: (h) => String(h || '').trim(),
							complete: (results) => {
								const { data } = results
								if (data && data.length > 0) {
									console.log(`Successfully loaded ${data.length} rows for ${mapId} from ${csvPath}`)
									setFullIngresData(data)
								} else {
									console.warn(`No data found in ${csvPath}`)
								}
								setIngresLoading(false)
							},
							error: (error) => {
								console.warn(`Error parsing CSV from ${csvPath}:`, error)
								setIngresLoading(false)
							}
						})
					} else {
						console.warn(`Failed to fetch ${csvPath}: ${response.status}`)
						setIngresLoading(false)
					}
				} catch (error) {
					console.warn(`Failed to load ${csvPath}:`, error)
					setIngresLoading(false)
				}
			}

			loadMapData()
		}
	}, [mapId, fullIngresData.length, ingresLoading])

	// Load dedicated CSV files for maps 2, 3, 4
	useEffect(() => {
		const csvFiles = {
			map2: '/Dashboard_CSV/RR_TOT_2024-2025.csv',  // Rainfall data
			map3: '/Dashboard_CSV/AGR_TOT_2024-2025.csv', // Annual Groundwater Recharge
			map4: '/Dashboard_CSV/AER_TOT_2024-2025.csv'  // Annual Extractable Resource
		}

		if (csvFiles[mapId] && fullIngresData.length === 0) {
			const loadDedicatedCSV = async () => {
				try {
					setIngresLoading(true)
					const response = await fetch(csvFiles[mapId])
					if (response.ok) {
						const csvText = await response.text()
						Papa.parse(csvText, {
							header: true,
							skipEmptyLines: true,
							complete: (results) => {
								console.log(`Loaded ${mapId} CSV:`, results.data.length, 'rows')
								setFullIngresData(results.data || [])
								setIngresLoading(false)
							},
							error: (error) => {
								console.warn(`Error parsing ${mapId} CSV:`, error)
								setIngresLoading(false)
							}
						})
					} else {
						console.warn(`Failed to fetch ${csvFiles[mapId]}: ${response.status}`)
						setIngresLoading(false)
					}
				} catch (error) {
					console.warn(`Failed to load ${csvFiles[mapId]}:`, error)
					setIngresLoading(false)
				}
			}

			loadDedicatedCSV()
		}
	}, [mapId, fullIngresData.length])

	// compute choropleth values depending on mapId
	const choroplethValues = useMemo(() => {
		// stronger normalizer: lower-case, expand '&' to 'and', remove punctuation, collapse spaces
		const normalize = (s) => String(s || '')
			.normalize('NFD') // decompose diacritics
			.replace(/\p{Diacritic}/gu, '')
			.toLowerCase()
			.replace(/&/g, ' and ')
			.replace(/[(){}:;,.\\"'`'–—•]/g, ' ')
			.replace(/[^a-z0-9\s]/g, ' ')
			.replace(/\s+/g, ' ')
			.trim()

		if (mapId === 'map1') {
			// build a map of STATE-DISTRICT => category from stageData (Stage of Extraction Total)
			const m = {}
			stageData.forEach(r => {
				const rawState = r.STATE || r.State || r.state || r['STATE_NAME'] || ''
				const rawDistrict = r.DISTRICT || r.District || r.district || r['DISTRICT_NAME'] || ''
				const val = parseFloat(r['Stage of Extraction Total'])
				// create several lookup variants for resilience
				const variants = new Set()
				variants.add(normalize(`${rawState}||${rawDistrict}`))
				if (rawDistrict) variants.add(normalize(rawDistrict))
				if (rawState) variants.add(normalize(rawState))
				variants.add(normalize(`${rawState} ${rawDistrict}`))
				variants.add(normalize(`${rawDistrict}, ${rawState}`))
				// also add spaceless forms
				if (rawDistrict) variants.add(normalize(rawDistrict).replace(/\s+/g, ''))
				variants.forEach(k => { if (k) m[k] = val })
			})
			return m
		} else {
			// Use dedicated CSV data for maps 2, 3, 4
			const targetField = mapId === 'map2' ? 'RR_Tot' : mapId === 'map3' ? 'AGR_Tot' : 'AER_Tot'
			const m = {}
			
			// Use fullIngresData (loaded from dedicated CSV files) for maps 2, 3, 4
			const dataToUse = fullIngresData.length > 0 ? fullIngresData : ingresData
			
			dataToUse.forEach(r => {
				if (!r || typeof r !== 'object') return
				
				const rawState = r.STATE || r.State || r.state || ''
				const rawDistrict = r.DISTRICT || r.District || r.district || ''
				const rawVal = r[targetField]
				
				const val = rawVal != null && rawVal !== '' ? parseFloat(String(rawVal).replace(/,/g, '')) : null
				
				if (val != null && !Number.isNaN(val)) {
					// Create multiple lookup variants for district/state matching
					const variants = new Set()
					variants.add(normalize(`${rawState}||${rawDistrict}`))
					if (rawDistrict) variants.add(normalize(rawDistrict))
					if (rawState) variants.add(normalize(rawState))
					variants.add(normalize(`${rawState} ${rawDistrict}`))
					variants.add(normalize(`${rawDistrict}, ${rawState}`))
					if (rawDistrict) variants.add(normalize(rawDistrict).replace(/\s+/g, ''))
					if (rawDistrict) variants.add(normalize(rawDistrict).replace(/\b(district|dist|districts)\b/g, '').replace(/\s+/g, ' ').trim())
					variants.forEach(k => { if (k) m[k] = val })
				}
			})
			return m
		}
	}, [mapId, stageData, ingresData, fullIngresData])



	const highlightStyle = { weight: 2.5, fillOpacity: 0.85, color: '#22d3ee', fillColor: '#22d3ee', fill: true }

	// helper to normalize strings and build a lookup key from feature properties
	const normalize = (s) => String(s || '')
		.normalize('NFD')
		.replace(/\p{Diacritic}/gu, '')
		.toLowerCase()
		.replace(/&/g, ' and ')
		.replace(/[(){}:;,.\\"'`'–—•]/g, ' ')
		.replace(/[^a-z0-9\s]/g, ' ')
		.replace(/\s+/g, ' ')
		.trim()

	// get the choropleth value for a geojson feature (tries state||district, then district only)
	const getFeatureValue = useCallback((feature) => {
		const props = feature.properties || {}
		const fState = props.NAME_1 || props.NAME_0 || props.STATE || props.state || props['STATE_NAME'] || ''
		// prefer NAME_2 for district, but try several fallbacks
		const fDistrict = props.NAME_2 || props.NAME_1 || props.NAME || props.DISTRICT || props.district || props['DISTRICT_NAME'] || ''
		const rawFeatureKey = `${fState}||${fDistrict}`
		const key = normalize(rawFeatureKey)
		// direct exact matches
		if (choroplethValues[key] != null) return choroplethValues[key]
		const districtKey = normalize(fDistrict)
		if (choroplethValues[districtKey] != null) return choroplethValues[districtKey]
		// try spaceless district
		const districtNoSpace = districtKey.replace(/\s+/g, '')
		if (choroplethValues[districtNoSpace] != null) return choroplethValues[districtNoSpace]
		// try state-only
		const stateKey = normalize(fState)
		if (choroplethValues[stateKey] != null) return choroplethValues[stateKey]
		// token-overlap fallback: try to find any choropleth key that contains all tokens of the district
		try {
			const tokens = districtKey.split(' ').filter(Boolean)
			if (tokens.length) {
				for (const k of Object.keys(choroplethValues)) {
					const matchesAll = tokens.every(t => k.includes(t))
					if (matchesAll) return choroplethValues[k]
				}
			}
		} catch (err) { 
			console.warn('Error in token matching:', err)
		}
		return null
	}, [choroplethValues])

	// style function used by GeoJSON to style each feature individually
	const styleForFeature = (feature) => {
	 	const value = getFeatureValue(feature)
		// base appearance: use a light-blue baseline so regions are visible even when data is missing
		const base = { color: '#084a72', weight: 1.0, fillOpacity: 0.6, fillColor: 'rgb(230,244,255)', fill: true }

	 	if (value != null && !Number.isNaN(value)) {
	 		if (mapId === 'map1') {
	 			const v = value
	 			let fill = '#10b981'
	 			if (v >= 100) fill = '#ef4444'
	 			else if (v >= 90) fill = '#f97316'
	 			else if (v >= 70) fill = '#f59e0b'
	 			return { ...base, fillColor: fill, color: fill, fillOpacity: 0.75 }
	 		} else {
				const vals = Object.values(choroplethValues).filter(v => v != null && !Number.isNaN(v))
				if (vals.length) {
					const min = Math.min(...vals)
					const max = Math.max(...vals)
					const t = max === min ? 0.5 : (value - min) / (max - min)
					const lerp = (a, b, t) => Math.round(a + (b - a) * t)
					let from, to, stroke, fillOpacity
					// choose ramps per map
					if (mapId === 'map2') {
						// blue ramp for rainfall (mm)
						from = [230, 244, 255]
						to = [3, 105, 161]
						stroke = '#023e58'
						fillOpacity = 0.95
					} else if (mapId === 'map3') {
						// green->yellow for AGR_Tot (recharge)
						from = [235, 250, 232]
						to = [159, 98, 0]
						stroke = '#3a6b2a'
						fillOpacity = 0.9
					} else {
						// purple->red for AER_Tot (extractable)
						from = [245, 240, 255]
						to = [109, 40, 217]
						stroke = '#6b21a8'
						fillOpacity = 0.92
					}
					const rgb = [lerp(from[0], to[0], t), lerp(from[1], to[1], t), lerp(from[2], to[2], t)]
					const fill = `rgb(${rgb.join(',')})`
					return { ...base, fillColor: fill, color: stroke, fillOpacity, fill: true }
				}
	 		}
	 	}

		// ensure even the base style explicitly enables fill
		return { ...base, fill: true }
	}

	const onEachFeature = (feature, layer) => {
		// identify matching key (STATE||DISTRICT) from feature properties
	 	const props = feature.properties || {}
 	  const value = getFeatureValue(feature)

 	  // derive readable names for tooltip (duplicate logic from getFeatureValue)
 	  const fState = props.NAME_1 || props.NAME_0 || props.STATE || props.state || props['STATE_NAME'] || ''
 	  const fDistrict = props.NAME_2 || props.NAME_1 || props.NAME || props.DISTRICT || props.district || props['DISTRICT_NAME'] || ''

		// default tooltip label
		let label = fDistrict || fState || props.NAME || props.name || 'Region'
		let extra = ''
		if (mapId === 'map1') {
			// For map1 show categorical stage-of-extraction with percent
			if (value != null && !Number.isNaN(value)) {
				const category = value >= 100 ? 'Over-Exploited' : value >= 90 ? 'Critical' : value >= 70 ? 'Semi-Critical' : value > 0 ? 'Safe' : 'Unknown'
				extra = ` — ${category} (${value}%)`
			}
		} else {
			// For maps 2, 3, 4 show appropriate labels and units
			if (value != null && !Number.isNaN(value)) {
				const formatted = Number.isFinite(value) ? (Math.round(value * 100) / 100).toString() : String(value)
				if (mapId === 'map2') {
					extra = ` — Rainfall: ${formatted} mm`
				} else if (mapId === 'map3') {
					extra = ` — Recharge: ${formatted} ham`
				} else if (mapId === 'map4') {
					extra = ` — Extractable: ${formatted} ham`
				} else {
					extra = ` — ${formatted}`
				}
			}
		}

		layer.bindTooltip(`${label}${extra}`, { sticky: true })
		layer.on({
			mouseover: () => layer.setStyle({ ...highlightStyle, fillOpacity: 0.6 }),
			mouseout: () => layer.setStyle(styleForFeature(feature)),
			click: () => {
				try { 
					layer.bringToFront() 
				} catch (err) { 
					console.warn('Error bringing layer to front:', err)
				}
				layer.setStyle({ color: '#22d3ee', fillColor: '#22d3ee' })
			},
		})
		// ensure initial style reflects data (styleForFeature handles this)
		layer.setStyle(styleForFeature(feature))
	}

	const bounds = useMemo(() => {
		// Approximate bounds around India
		return [
			[6.5, 68.0],
			[37.5, 97.5],
		]
	}, [])

	useEffect(() => {
		// Fit to bounds when geojson mounts
		const layer = geoJsonRef.current
		if (layer && layer._map) {
			try {
				layer._map.fitBounds(bounds, { padding: [20, 20] })
			} catch (error) {
				// Map might not be ready for fitBounds
				console.debug('Could not fit bounds:', error)
			}
		}
	}, [bounds])

	// Try to fetch a real India GeoJSON from common public locations. This lets users drop a file in `public/`.
	useEffect(() => {
		const candidates = [
			'/india_district.geojson',
			'/india_districts.geojson',
			'/india_state.geojson',
			'/india_states_districts.geojson',
			'/india_telengana.geojson',
			'/geojson/india_districts.geojson',
			'/data/india_districts.geojson',
		]

		let cancelled = false
		const tried = []
		async function tryLoad() {
			for (const p of candidates) {
				try {
					const res = await fetch(p)
					tried.push({ path: p, status: res.status })
					if (!res.ok) continue
					const json = await res.json()
					if (cancelled) return
					setPublicGeoJson(json)
					setGeoJsonError(null)
					return
				} catch (err) {
					tried.push({ path: p, error: 'fetch error' })
					console.warn(`Failed to load GeoJSON from ${p}:`, err)
					// try next
				}
			}
			if (!cancelled) {
				setGeoJsonError('No public GeoJSON found; drop a GeoJSON into client/public (e.g. india_district.geojson) to enable district choropleth. Tried: ' + candidates.join(', '))
			}
		}
		tryLoad()
		return () => { cancelled = true }
	}, [getFeatureValue])


	// Enhanced legend for all map types
	const Legend = () => {
		if (!choroplethValues) return null
		const vals = Object.values(choroplethValues).filter(v => v != null && !Number.isNaN(v))
		if (vals.length === 0) return null

		if (mapId === 'map1') {
			// Categorical legend for Stage of Extraction
			const categories = [
				{ label: 'Safe', color: '#10b981', range: '< 70%' },
				{ label: 'Semi-Critical', color: '#f59e0b', range: '70-90%' },
				{ label: 'Critical', color: '#f97316', range: '90-100%' },
				{ label: 'Over-Exploited', color: '#ef4444', range: '> 100%' }
			]
			
			return (
				<div className="absolute right-3 bottom-3 bg-slate-800/85 text-xs text-slate-100 rounded-lg p-3 shadow-lg">
					<div className="font-medium mb-2 text-slate-200">Stage of Extraction</div>
					{categories.map((cat, i) => (
						<div key={i} className="flex items-center gap-2 mb-1">
							<div 
								className="w-4 h-3 rounded-sm border border-slate-600" 
								style={{ backgroundColor: cat.color }}
							/>
							<span className="text-slate-200">{cat.label}</span>
							<span className="text-slate-400 text-xs">({cat.range})</span>
						</div>
					))}
					<div className="text-slate-400 text-xs mt-2 pt-2 border-t border-slate-600">
						{vals.length} districts
					</div>
				</div>
			)
		}

		// Continuous legend for maps 2, 3, 4
		const min = Math.min(...vals)
		const max = Math.max(...vals)
		const range = max - min
		
		// Create 5 color bands with ranges
		const bands = []
		for (let i = 0; i < 5; i++) {
			const t = i / 4
			const lerp = (a, b, t) => Math.round(a + (b - a) * t)
			let from, to
			if (mapId === 'map2') { from = [230, 244, 255]; to = [3, 105, 161] }
			else if (mapId === 'map3') { from = [235, 250, 232]; to = [159, 98, 0] }
			else { from = [245, 240, 255]; to = [109, 40, 217] }
			const rgb = [lerp(from[0], to[0], t), lerp(from[1], to[1], t), lerp(from[2], to[2], t)]
			const color = `rgb(${rgb.join(',')})`
			
			const rangeStart = min + (range / 5) * i
			const rangeEnd = min + (range / 5) * (i + 1)
			
			bands.push({
				color,
				range: i === 4 ? `${rangeStart.toFixed(1)} - ${rangeEnd.toFixed(1)}` : `${rangeStart.toFixed(1)} - ${rangeEnd.toFixed(1)}`
			})
		}

		const getMapInfo = () => {
			switch (mapId) {
				case 'map2': return { title: 'Annual Rainfall', unit: 'mm' }
				case 'map3': return { title: 'Annual Recharge', unit: 'ham' }
				case 'map4': return { title: 'Annual Extractable', unit: 'ham' }
				default: return { title: 'Data Range', unit: '' }
			}
		}

		const { title, unit } = getMapInfo()
		
		return (
			<div className="absolute right-3 bottom-3 bg-slate-800/85 text-xs text-slate-100 rounded-lg p-3 shadow-lg min-w-48">
				<div className="font-medium mb-3 text-slate-200">{title}</div>
				{bands.map((band, i) => (
					<div key={i} className="flex items-center gap-2 mb-1.5">
						<div 
							className="w-4 h-3 rounded-sm border border-slate-600" 
							style={{ backgroundColor: band.color }}
						/>
						<span className="text-slate-300 text-xs">
							{band.range} {unit}
						</span>
					</div>
				))}
				<div className="text-slate-400 text-xs pt-2 border-t border-slate-600">
					{vals.length} districts
				</div>
			</div>
		)
	}

	return (
		<div className="relative h-80 md:h-96 lg:h-[450px] rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl overflow-hidden shadow-lg hover:shadow-cyan-500/25 transition-all duration-300">
			{geoJsonError && (
				<div className="absolute left-3 top-3 z-20 text-xs text-amber-300 bg-slate-900/80 backdrop-blur-sm px-3 py-2 rounded-lg border border-amber-500/20">{geoJsonError}</div>
			)}
			{ingresLoading && mapId !== 'map1' && (
				<div className="absolute left-3 bottom-3 z-20 text-xs text-cyan-300 bg-slate-900/80 backdrop-blur-sm px-3 py-2 rounded-lg border border-cyan-500/20">Loading INGRES data...</div>
			)}
			<MapContainer
				className="h-full w-full"
				center={[22.5, 80]}
				zoom={4}
				minZoom={3}
				maxZoom={8}
				zoomControl={true}
				attributionControl={false}
				style={{ height: '100%', width: '100%' }}
			>
				<TileLayer
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					opacity={0.35}
				/>
				{publicGeoJson && (
					<GeoJSON data={publicGeoJson} style={styleForFeature} onEachFeature={onEachFeature} ref={geoJsonRef} />
				)}
			</MapContainer>
			<Legend />
		</div>
	)
}
