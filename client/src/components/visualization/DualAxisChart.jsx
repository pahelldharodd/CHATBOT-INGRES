import { useMemo, useState } from 'react'
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const DualAxisChart = ({ data }) => {
  const [viewType, setViewType] = useState('both') // 'district', 'state', 'both'
  const [selectedStates, setSelectedStates] = useState([])
  const [selectedDistricts, setSelectedDistricts] = useState([])
  const [selectAllStates, setSelectAllStates] = useState(true)
  const [selectAllDistricts, setSelectAllDistricts] = useState(true)
  const [sortType, setSortType] = useState('all') // 'top20', 'bottom20', 'all'

  // Get unique states and districts
  const uniqueStates = useMemo(() => {
    return [...new Set(data.map(item => item.STATE))].sort()
  }, [data])

  const uniqueDistricts = useMemo(() => {
    return [...new Set(data.map(item => item.DISTRICT))].sort()
  }, [data])

  // Initialize selected states and districts
  useMemo(() => {
    if (selectAllStates && selectedStates.length === 0) {
      setSelectedStates(uniqueStates)
    }
    if (selectAllDistricts && selectedDistricts.length === 0) {
      setSelectedDistricts(uniqueDistricts)
    }
  }, [uniqueStates, uniqueDistricts, selectAllStates, selectAllDistricts, selectedStates.length, selectedDistricts.length])

  // Process data based on view type and filters
  const chartData = useMemo(() => {
    let filteredData = data.filter(item => {
      const stateMatch = selectAllStates || selectedStates.includes(item?.STATE)
      const districtMatch = selectAllDistricts || selectedDistricts.includes(item?.DISTRICT)
      return stateMatch && districtMatch
    })

    let processedData = []

    if (viewType === 'state') {
      // Group by state
      const stateData = {}
      filteredData.forEach(item => {
        if (!stateData[item.STATE]) {
          stateData[item.STATE] = {
            name: item.STATE,
            annualResource: 0,
            extraction: 0,
            count: 0
          }
        }
        stateData[item.STATE].annualResource += parseFloat(item['Annual Extractable Ground water Resource (ham)Total'] || 0)
        stateData[item.STATE].extraction += parseFloat(item['Ground Water Extraction for all uses (ha.m) Total'] || 0)
        stateData[item.STATE].count++
      })
      
      processedData = Object.values(stateData)
    } else if (viewType === 'district') {
      // Show districts
      processedData = filteredData.map(item => ({
        name: item.DISTRICT,
        state: item.STATE,
        annualResource: parseFloat(item['Annual Extractable Ground water Resource (ham)Total'] || 0),
        extraction: parseFloat(item['Ground Water Extraction for all uses (ha.m) Total'] || 0)
      }))
    } else {
      // Show both - combine state and district names
      processedData = filteredData.map(item => ({
        name: `${item.STATE} - ${item.DISTRICT}`,
        state: item.STATE,
        district: item.DISTRICT,
        annualResource: parseFloat(item['Annual Extractable Ground water Resource (ham)Total'] || 0),
        extraction: parseFloat(item['Ground Water Extraction for all uses (ha.m) Total'] || 0)
      }))
    }

    // Apply sorting based on sortType
    if (sortType === 'top20') {
      return processedData
        .sort((a, b) => (b.annualResource + b.extraction) - (a.annualResource + a.extraction))
        .slice(0, 20)
    } else if (sortType === 'bottom20') {
      return processedData
        .sort((a, b) => (a.annualResource + a.extraction) - (b.annualResource + b.extraction))
        .slice(0, 20)
    } else {
      // 'all' - sort alphabetically and limit to 20
      return processedData
        .sort((a, b) => (a.name || '').localeCompare(b.name || ''))
        .slice(0, 20)
    }
  }, [data, viewType, selectedStates, selectedDistricts, selectAllStates, selectAllDistricts, sortType])

  const handleStateToggle = (state) => {
    if (selectAllStates) {
      // If all are selected, deselect all and select only this one
      setSelectAllStates(false)
      setSelectedStates([state])
    } else {
      const newSelected = selectedStates.includes(state)
        ? selectedStates.filter(s => s !== state)
        : [...selectedStates, state]
      
      setSelectedStates(newSelected)
      // If all items are now selected, set selectAll to true
      if (newSelected.length === uniqueStates.length) {
        setSelectAllStates(true)
      }
    }
  }

  const handleDistrictToggle = (district) => {
    if (selectAllDistricts) {
      // If all are selected, deselect all and select only this one
      setSelectAllDistricts(false)
      setSelectedDistricts([district])
    } else {
      const newSelected = selectedDistricts.includes(district)
        ? selectedDistricts.filter(d => d !== district)
        : [...selectedDistricts, district]
      
      setSelectedDistricts(newSelected)
      // If all items are now selected, set selectAll to true
      if (newSelected.length === uniqueDistricts.length) {
        setSelectAllDistricts(true)
      }
    }
  }

  const handleSelectAllStates = () => {
    if (selectAllStates) {
      // Currently all selected, so deselect all
      setSelectAllStates(false)
      setSelectedStates([])
    } else {
      // Currently not all selected, so select all
      setSelectAllStates(true)
      setSelectedStates(uniqueStates)
    }
  }

  const handleSelectAllDistricts = () => {
    if (selectAllDistricts) {
      // Currently all selected, so deselect all
      setSelectAllDistricts(false)
      setSelectedDistricts([])
    } else {
      // Currently not all selected, so select all
      setSelectAllDistricts(true)
      setSelectedDistricts(uniqueDistricts)
    }
  }

  const formatValue = (value) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
    return value.toFixed(1)
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/80 backdrop-blur-xl border border-cyan-500/30 rounded-xl p-4 shadow-2xl shadow-cyan-500/10">
          <p className="text-slate-100 font-semibold mb-2 text-sm">{label}</p>
          {payload.map((entry, index) => (
            <p key={`${(entry && entry.name) ? entry.name : 'payload'}__${index}`} className="text-xs text-slate-200" style={{ color: entry.color }}>
              {entry.name}: {formatValue(entry.value)} BCM
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 hover:bg-slate-800/60 hover:border-cyan-400/40 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-100 mb-4 text-glow">
          Groundwater Resources vs Extraction Analysis
        </h2>
        
        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
          {/* View Type Filter */}
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10 hover:border-cyan-400/30 transition-all duration-300">
            <label className="block text-base font-semibold text-slate-200 mb-3">View Type</label>
            <select
              value={viewType}
              onChange={(e) => setViewType(e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 backdrop-blur-sm border border-cyan-500/20 rounded-lg text-slate-100 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 hover:border-cyan-400/40 transition-all duration-200 text-sm font-medium"
            >
              <option value="district">District View</option>
              <option value="state">State View</option>
              <option value="both">Combined View</option>
            </select>
          </div>

          {/* Sort Type Filter */}
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10 hover:border-cyan-400/30 transition-all duration-300">
            <label className="block text-base font-semibold text-slate-200 mb-3">Sort By</label>
            <select
              value={sortType}
              onChange={(e) => setSortType(e.target.value)}
              className="w-full px-4 py-3 bg-slate-700/50 backdrop-blur-sm border border-cyan-500/20 rounded-lg text-slate-100 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 hover:border-cyan-400/40 transition-all duration-200 text-sm font-medium"
            >
              <option value="all">Alphabetical A-Z</option>
              <option value="top20">Top 20 Resources</option>
              <option value="bottom20">Bottom 20 Resources</option>
            </select>
          </div>

          {/* States Filter */}
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10 hover:border-cyan-400/30 transition-all duration-300">
            <label className="block text-base font-semibold text-slate-200 mb-3">Filter States</label>
            <div className="bg-slate-700/40 backdrop-blur-sm border border-cyan-500/20 rounded-lg p-3 max-h-52 overflow-y-auto glass-scrollbar">
              <label className="flex items-center gap-3 mb-3 sticky top-0 bg-slate-700/60 backdrop-blur-sm pb-2 border-b border-cyan-500/20">
                <input
                  type="checkbox"
                  checked={selectAllStates}
                  onChange={handleSelectAllStates}
                  className="w-4 h-4 rounded border-cyan-500/30 text-cyan-500 focus:ring-2 focus:ring-cyan-500 bg-slate-600/60"
                />
                <span className="text-sm text-slate-100 font-semibold">All States ({uniqueStates.length})</span>
              </label>
              <div className="space-y-2">
                {uniqueStates.map((state, i) => (
                  <label key={`${state || 'state'}__${i}`} className="flex items-center gap-3 py-2 px-2 rounded-md hover:bg-cyan-500/10 cursor-pointer transition-colors duration-150">
                    <input
                      type="checkbox"
                      checked={selectAllStates || selectedStates.includes(state)}
                      onChange={() => handleStateToggle(state)}
                      className="w-4 h-4 rounded border-cyan-500/30 text-cyan-500 focus:ring-2 focus:ring-cyan-500 bg-slate-600/60 flex-shrink-0"
                    />
                    <span className="text-sm text-slate-200 leading-relaxed truncate font-medium" title={state}>{state}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Districts Filter */}
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10 hover:border-cyan-400/30 transition-all duration-300">
            <label className="block text-base font-semibold text-slate-200 mb-3">Filter Districts</label>
            <div className="bg-slate-700/40 backdrop-blur-sm border border-cyan-500/20 rounded-lg p-3 max-h-52 overflow-y-auto glass-scrollbar">
              <label className="flex items-center gap-3 mb-3 sticky top-0 bg-slate-700/60 backdrop-blur-sm pb-2 border-b border-cyan-500/20">
                <input
                  type="checkbox"
                  checked={selectAllDistricts}
                  onChange={handleSelectAllDistricts}
                  className="w-4 h-4 rounded border-cyan-500/30 text-cyan-500 focus:ring-2 focus:ring-cyan-500 bg-slate-600/60"
                />
                <span className="text-sm text-slate-100 font-semibold">All Districts ({uniqueDistricts.length})</span>
              </label>
              <div className="space-y-2">
                {uniqueDistricts.map((district, i) => (
                  <label key={`${district || 'district'}__${i}`} className="flex items-center gap-3 py-2 px-2 rounded-md hover:bg-cyan-500/10 cursor-pointer transition-colors duration-150">
                    <input
                      type="checkbox"
                      checked={selectAllDistricts || selectedDistricts.includes(district)}
                      onChange={() => handleDistrictToggle(district)}
                      className="w-4 h-4 rounded border-cyan-500/30 text-cyan-500 focus:ring-2 focus:ring-cyan-500 bg-slate-600/60 flex-shrink-0"
                    />
                    <span className="text-sm text-slate-200 leading-relaxed truncate font-medium" title={district}>{district}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-lg p-3 border border-cyan-500/10 mb-4">
          <p className="text-sm text-slate-200 font-medium">
            Showing <span className="text-cyan-400 font-bold">{chartData.length}</span> {viewType === 'state' ? 'states' : viewType === 'district' ? 'districts' : 'entries'}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[450px] md:h-[550px] lg:h-[650px] xl:h-[700px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ 
              top: 40, 
              right: 120, 
              left: 120, 
              bottom: chartData.length > 15 ? 140 : chartData.length > 10 ? 120 : 100
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" strokeOpacity={0.3} />
            <XAxis
              dataKey="name"
              angle={-40}
              textAnchor="end"
              height={chartData.length > 15 ? 140 : chartData.length > 10 ? 120 : 100}
              tick={{ fontSize: 11, fill: '#cbd5e1' }}
              interval={0}
              tickMargin={10}
              axisLine={{ stroke: '#64748b' }}
              tickLine={{ stroke: '#64748b' }}
            />
            <YAxis
              yAxisId="left"
              orientation="left"
              domain={[0, 'dataMax']}
              tick={{ fontSize: 11, fill: '#cbd5e1' }}
              tickFormatter={(value) => {
                if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
                if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
                return value.toFixed(0)
              }}
              label={{ 
                value: 'Annual Resource (BCM)', 
                angle: -90, 
                position: 'outside',
                offset: -20,
                style: { 
                  textAnchor: 'middle', 
                  fill: '#06b6d4', 
                  fontSize: '12px',
                  fontWeight: '600'
                } 
              }}
              width={95}
              tickMargin={10}
              axisLine={{ stroke: '#64748b' }}
              tickLine={{ stroke: '#64748b' }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              domain={[0, 420]}
              tick={{ fontSize: 11, fill: '#cbd5e1' }}
              tickFormatter={(value) => {
                if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
                return value.toFixed(0)
              }}
              label={{ 
                value: 'Extraction (BCM)', 
                angle: 90, 
                position: 'outside',
                offset: 20,
                style: { 
                  textAnchor: 'middle', 
                  fill: '#14b8a6', 
                  fontSize: '12px',
                  fontWeight: '600'
                } 
              }}
              width={95}
              tickMargin={10}
              axisLine={{ stroke: '#64748b' }}
              tickLine={{ stroke: '#64748b' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ 
                paddingTop: '15px', 
                fontSize: '12px',
                color: '#cbd5e1'
              }}
              iconType="rect"
              layout="horizontal"
              verticalAlign="top"
            />
            <Bar
              yAxisId="left"
              dataKey="annualResource"
              fill="#3b82f6"
              name="Annual Resource (BCM)"
              opacity={0.8}
              radius={[2, 2, 0, 0]}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="extraction"
              stroke="#ef4444"
              strokeWidth={2.5}
              name="Extraction (BCM)"
              dot={{ fill: '#ef4444', strokeWidth: 2, r: 3 }}
              activeDot={{ r: 5, stroke: '#ef4444', strokeWidth: 2, fill: '#fff' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <p className="text-xs text-slate-500 mt-2 text-center">
        {sortType === 'all' 
          ? `Chart shows first 20 entries alphabetically. Total available: ${chartData.length === 20 ? '20+' : chartData.length}` 
          : `Showing ${sortType === 'top20' ? 'top' : 'bottom'} 20 entries by combined resource and extraction values`
        }
      </p>
    </div>
  )
}

export default DualAxisChart
