import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

const API_BASE = "http://localhost:7862";

export default function PredictionPage() {
  const [selectedState, setSelectedState] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [reportGenerated, setReportGenerated] = useState(false);

  useEffect(() => {
    // Sample states data
    const sampleStates = [
      "ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR", "CHHATTISGARH",
      "GOA", "GUJARAT", "HARYANA", "HIMACHAL PRADESH", "JHARKHAND", "KARNATAKA",
      "KERALA", "MADHYA PRADESH", "MAHARASHTRA", "MANIPUR", "MEGHALAYA", "MIZORAM",
      "NAGALAND", "ODISHA", "PUNJAB", "RAJASTHAN", "SIKKIM", "TAMIL NADU",
      "TELANGANA", "TRIPURA", "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL"
    ];
    setStates(sampleStates);
  }, []);

  useEffect(() => {
    const sampleDistricts = {
      "ANDHRA PRADESH": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
      "GUJARAT": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udepur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kachchh", "Kheda", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
      "MAHARASHTRA": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"]
    };
    
    if (selectedState && sampleDistricts[selectedState]) {
      setDistricts(sampleDistricts[selectedState]);
      setSelectedDistrict("");
    }
  }, [selectedState]);

  // Generate mock prediction data with realistic patterns
  const generatePredictionData = () => {
    const currentYear = new Date().getFullYear();
    const historicalYears = 10;
    const predictionYears = 20;
    
    // Base extraction rate with some randomness
    const baseExtractionRate = Math.random() * 50 + 30; // 30-80%
    const currentExtractionRate = baseExtractionRate + (Math.random() * 20 - 10);
    
    // Generate historical data with trend
    const historicalData = [];
    for (let i = historicalYears; i >= 0; i--) {
      const year = currentYear - i;
      const trendFactor = (historicalYears - i) / historicalYears;
      const extraction = Math.max(10, baseExtractionRate + (trendFactor * 20) + (Math.random() * 10 - 5));
      const recharge = Math.max(5, 40 - (trendFactor * 15) + (Math.random() * 8 - 4));
      
      historicalData.push({
        year,
        extraction: Math.round(extraction * 100) / 100,
        recharge: Math.round(recharge * 100) / 100,
        netDepletion: Math.round((extraction - recharge) * 100) / 100,
        type: "historical"
      });
    }

    // Generate prediction data
    const predictionData = [];
    let lastExtraction = historicalData[historicalData.length - 1].extraction;
    let lastRecharge = historicalData[historicalData.length - 1].recharge;
    
    for (let i = 1; i <= predictionYears; i++) {
      const year = currentYear + i;
      // Simulate increasing extraction and decreasing recharge
      lastExtraction = Math.min(95, lastExtraction + (Math.random() * 3 + 1));
      lastRecharge = Math.max(5, lastRecharge - (Math.random() * 1.5));
      
      predictionData.push({
        year,
        extraction: Math.round(lastExtraction * 100) / 100,
        recharge: Math.round(lastRecharge * 100) / 100,
        netDepletion: Math.round((lastExtraction - lastRecharge) * 100) / 100,
        type: "prediction"
      });
    }

    const allData = [...historicalData, ...predictionData];
    
    // Calculate depletion year
    const depletionYear = predictionData.find(d => d.extraction >= 90)?.year || null;
    const yearsLeft = depletionYear ? depletionYear - currentYear : null;
    
    // Generate alerts based on patterns
    const generatedAlerts = [];
    const recentGrowth = (currentExtractionRate - historicalData[0].extraction) / historicalYears;
    
    if (recentGrowth > 2) {
      generatedAlerts.push({
        type: "critical",
        message: `Critical: Extraction rate increasing by ${recentGrowth.toFixed(1)}% annually`,
        priority: "high"
      });
    }
    
    if (currentExtractionRate > 70) {
      generatedAlerts.push({
        type: "warning",
        message: `Warning: Current extraction rate at ${currentExtractionRate.toFixed(1)}% - approaching critical levels`,
        priority: "medium"
      });
    }
    
    if (yearsLeft && yearsLeft < 10) {
      generatedAlerts.push({
        type: "urgent",
        message: `Urgent: Complete depletion predicted in ${yearsLeft} years`,
        priority: "critical"
      });
    }

    // Risk assessment
    let riskLevel = "Low";
    let riskColor = "#10b981";
    if (currentExtractionRate > 50 && currentExtractionRate <= 70) {
      riskLevel = "Medium";
      riskColor = "#f59e0b";
    } else if (currentExtractionRate > 70 && currentExtractionRate <= 85) {
      riskLevel = "High";
      riskColor = "#ef4444";
    } else if (currentExtractionRate > 85) {
      riskLevel = "Critical";
      riskColor = "#dc2626";
    }

    return {
      timeSeriesData: allData,
      currentExtractionRate: Math.round(currentExtractionRate * 100) / 100,
      yearsLeft,
      depletionYear,
      riskLevel,
      riskColor,
      alerts: generatedAlerts,
      summary: {
        totalExtractionRate: Math.round(currentExtractionRate * 100) / 100,
        averageRecharge: Math.round(lastRecharge * 100) / 100,
        netDepletionRate: Math.round((currentExtractionRate - lastRecharge) * 100) / 100,
        trendDirection: recentGrowth > 0 ? "Increasing" : "Decreasing"
      }
    };
  };

  const handlePredict = async () => {
    if (!selectedState || !selectedDistrict) {
      alert("Please select both state and district");
      return;
    }

    setLoading(true);
    console.log('Starting prediction for:', selectedState, selectedDistrict);
    
    try {
      console.log('Making API call to:', `${API_BASE}/prediction/analyze`);
      
      const response = await fetch(`${API_BASE}/prediction/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          state: selectedState,
          district: selectedDistrict,
          years_ahead: 20
        }),
      });

      console.log('API Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error details:', errorText);
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('API Response data:', data);
      
      // Transform API response to match our component structure
      const transformedData = {
        timeSeriesData: data.time_series_data || [],
        currentExtractionRate: data.current_extraction_rate || 0,
        yearsLeft: data.years_left,
        depletionYear: data.predicted_depletion_year,
        riskLevel: data.risk_level || 'Unknown',
        riskColor: data.risk_color || '#64748b',
        alerts: data.alerts || [],
        summary: data.summary || {}
      };
      
      console.log('Transformed data:', transformedData);
      
      setPredictionData(transformedData);
      setAlerts(data.alerts || []);
      setReportGenerated(true);
      
      console.log('Prediction completed successfully');
    } catch (error) {
      console.error('Prediction failed:', error);
      console.log('Falling back to demo data');
      
      // Fallback to mock data if API fails
      const prediction = generatePredictionData();
      setPredictionData(prediction);
      setAlerts(prediction.alerts);
      setReportGenerated(true);
      
      // Show more detailed error message
      alert(`API call failed: ${error.message}\n\nUsing demo data instead. Please check:\n1. ML service is running on port 7862\n2. Network connectivity\n3. Browser console for detailed errors`);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    if (!predictionData) return;
    
    const reportData = {
      location: `${selectedDistrict}, ${selectedState}`,
      generatedOn: new Date().toISOString(),
      prediction: predictionData,
      alerts: alerts
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `groundwater-prediction-${selectedDistrict}-${selectedState}-${new Date().getFullYear()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const riskData = predictionData ? [
    { name: "Safe", value: predictionData.riskLevel === "Low" ? 100 : 0, color: "#10b981" },
    { name: "Medium Risk", value: predictionData.riskLevel === "Medium" ? 100 : 0, color: "#f59e0b" },
    { name: "High Risk", value: predictionData.riskLevel === "High" ? 100 : 0, color: "#ef4444" },
    { name: "Critical", value: predictionData.riskLevel === "Critical" ? 100 : 0, color: "#dc2626" }
  ].filter(item => item.value > 0) : [];

  return (
    <div className="min-h-screen bg-[#030714] relative pt-20">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-8 glass-scrollbar">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-100 mb-4 text-glow">
            Groundwater Depletion Prediction System
          </h1>
          <p className="text-slate-300 text-lg max-w-3xl mx-auto">
            Advanced ML-powered analysis to predict groundwater depletion patterns, generate alerts for abnormal extraction rates, and estimate years until complete resource depletion.
          </p>
        </div>

        {/* Selection Panel */}
        <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 mb-8 shadow-lg">
          <h2 className="text-xl font-semibold text-teal-300 mb-4">Location Selection</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Select State</label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full rounded-lg border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl px-4 py-3 text-slate-100 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
              >
                <option value="">Choose State</option>
                {states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Select District</label>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                disabled={!selectedState}
                className="w-full rounded-lg border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl px-4 py-3 text-slate-100 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all disabled:opacity-50"
              >
                <option value="">Choose District</option>
                {districts.map(district => (
                  <option key={district} value={district}>{district}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={handlePredict}
                disabled={loading || !selectedState || !selectedDistrict}
                className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-600 to-teal-600 border border-cyan-500/30 text-white font-semibold hover:from-cyan-500 hover:to-teal-500 hover:border-cyan-300/40 hover:shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing...
                  </div>
                ) : (
                  "Generate Prediction"
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Alerts Panel */}
        {alerts.length > 0 && (
          <div className="rounded-2xl border border-red-500/20 bg-slate-900/40 backdrop-blur-xl p-6 mb-8 shadow-lg">
            <h2 className="text-xl font-semibold text-red-300 mb-4 flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              Critical Alerts
            </h2>
            <div className="space-y-3">
              {alerts.map((alert, index) => (
                <div key={index} className={`p-4 rounded-lg border ${
                  alert.priority === "critical" ? "border-red-500/30 bg-red-900/20" :
                  alert.priority === "high" ? "border-orange-500/30 bg-orange-900/20" :
                  "border-yellow-500/30 bg-yellow-900/20"
                } backdrop-blur-sm`}>
                  <div className="flex items-center gap-3">
                    <span className="text-lg">
                      {alert.icon || 
                       (alert.priority === "critical" ? "🚨" : 
                        alert.priority === "high" ? "⚠️" : "⚡")}
                    </span>
                    <div className="flex-1">
                      <span className="text-slate-200">{alert.message}</span>
                      {alert.type && (
                        <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                          alert.type === "critical" ? "bg-red-500/20 text-red-300" :
                          alert.type === "warning" ? "bg-orange-500/20 text-orange-300" :
                          alert.type === "trend" ? "bg-blue-500/20 text-blue-300" :
                          "bg-yellow-500/20 text-yellow-300"
                        }`}>
                          {alert.type.toUpperCase()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Prediction Results */}
        {predictionData && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Current Extraction Rate</p>
                    <p className="text-2xl font-bold text-cyan-300">{predictionData.currentExtractionRate}%</p>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-cyan-500/20 flex items-center justify-center">
                    <span className="text-2xl">📊</span>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-teal-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Years Until Depletion</p>
                    <p className="text-2xl font-bold text-teal-300">
                      {predictionData.yearsLeft ? `${predictionData.yearsLeft} years` : "Not predicted"}
                    </p>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-teal-500/20 flex items-center justify-center">
                    <span className="text-2xl">⏰</span>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-orange-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Risk Level</p>
                    <p className="text-2xl font-bold" style={{ color: predictionData.riskColor }}>
                      {predictionData.riskLevel}
                    </p>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center">
                    <span className="text-2xl">🎯</span>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-green-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400">Net Depletion Rate</p>
                    <p className="text-2xl font-bold text-green-300">{predictionData.summary.netDepletionRate}%</p>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                    <span className="text-2xl">💧</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Time Series Chart */}
              <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
                <h3 className="text-lg font-semibold text-slate-200 mb-4">Extraction vs Recharge Trends</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={predictionData.timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="year" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                        border: '1px solid rgba(6, 182, 212, 0.3)',
                        borderRadius: '8px',
                        color: '#e2e8f0'
                      }} 
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="extraction" 
                      stroke="#ef4444" 
                      strokeWidth={2}
                      name="Extraction Rate (%)"
                      dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="recharge" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      name="Recharge Rate (%)"
                      dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Risk Assessment Pie Chart */}
              <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
                <h3 className="text-lg font-semibold text-slate-200 mb-4">Risk Assessment</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name }) => name}
                    >
                      {riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 text-center">
                  <p className="text-lg font-semibold" style={{ color: predictionData.riskColor }}>
                    Current Risk Level: {predictionData.riskLevel}
                  </p>
                </div>
              </div>
            </div>

            {/* Report Generation */}
            <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-200">Prediction Report</h3>
                {reportGenerated && (
                  <button
                    onClick={downloadReport}
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-green-600 to-emerald-600 border border-green-500/30 text-white font-medium hover:from-green-500 hover:to-emerald-500 transition-all duration-300"
                  >
                    📥 Download Report
                  </button>
                )}
              </div>
              
              <div className="space-y-4 text-slate-300">
                <div>
                  <h4 className="font-semibold text-slate-200 mb-2">Location Analysis: {selectedDistrict}, {selectedState}</h4>
                  <p>Current extraction rate of {predictionData.currentExtractionRate}% indicates {predictionData.riskLevel.toLowerCase()} risk level for groundwater sustainability.</p>
                </div>
                
                <div>
                  <h4 className="font-semibold text-slate-200 mb-2">Trend Analysis</h4>
                  <p>Extraction trend is {predictionData.summary.trendDirection.toLowerCase()} while recharge rate averages {predictionData.summary.averageRecharge}% annually.</p>
                </div>
                
                {predictionData.yearsLeft && (
                  <div>
                    <h4 className="font-semibold text-slate-200 mb-2">Depletion Forecast</h4>
                    <p>Based on current trends, complete groundwater depletion is predicted by {predictionData.depletionYear} ({predictionData.yearsLeft} years from now).</p>
                  </div>
                )}
                
                <div>
                  <h4 className="font-semibold text-slate-200 mb-2">Recommendations</h4>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Implement water conservation measures immediately</li>
                    <li>Monitor extraction rates monthly</li>
                    <li>Explore alternative water sources</li>
                    <li>Enhance rainwater harvesting systems</li>
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Instructions */}
        {!predictionData && (
          <div className="rounded-2xl border border-slate-600/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">How It Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-slate-300">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-cyan-500/20 flex items-center justify-center">
                  <span className="text-2xl">🎯</span>
                </div>
                <h4 className="font-semibold text-slate-200 mb-2">Select Location</h4>
                <p className="text-sm">Choose the state and district you want to analyze for groundwater depletion patterns.</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-teal-500/20 flex items-center justify-center">
                  <span className="text-2xl">🧠</span>
                </div>
                <h4 className="font-semibold text-slate-200 mb-2">ML Analysis</h4>
                <p className="text-sm">Our machine learning model analyzes historical data and predicts future depletion scenarios.</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-orange-500/20 flex items-center justify-center">
                  <span className="text-2xl">📊</span>
                </div>
                <h4 className="font-semibold text-slate-200 mb-2">Get Insights</h4>
                <p className="text-sm">Receive detailed predictions, alerts, and downloadable reports for informed decision making.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}