import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import OverviewCard from "../components/dashboard/OverviewCard";
import DataSummary from "../components/dashboard/DataSummary";
import GroundwaterMap from "../components/visualization/GroundwaterMap";
import DualAxisChart from "../components/visualization/DualAxisChart";
import { useI18n } from "../i18n/I18nContext";

function Modal({ open, onClose, title, children }) {
  return (
    <div
      className={`${
        open
          ? "opacity-100 pointer-events-auto"
          : "opacity-0 pointer-events-none"
      } fixed inset-0 z-50 transition-opacity duration-200`}
    >
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="absolute inset-0 grid place-items-center p-4">
        <div
          className={`${
            open
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-2"
          } w-full max-w-5xl max-h-[85vh] rounded-2xl border border-cyan-500/30 bg-slate-900/80 backdrop-blur-2xl shadow-2xl shadow-cyan-500/10 transition-all duration-300 flex flex-col`}
        >
          <div className="flex items-center justify-between px-6 py-5 border-b border-cyan-500/20 flex-shrink-0">
            <h3 className="text-xl font-bold text-slate-100 text-glow">{title}</h3>
            <button
              onClick={onClose}
              className="rounded-xl px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-700/60 backdrop-blur-sm border border-transparent hover:border-cyan-500/30 transition-all duration-300 text-lg font-bold"
            >
              ✕
            </button>
          </div>
          <div className="p-5 overflow-y-auto flex-1 glass-scrollbar">{children}</div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { t } = useI18n();
  const [mergedOpen, setMergedOpen] = useState(false);
  const [kpiOpen, setKpiOpen] = useState(null);
  const [dataById, setDataById] = useState({});
  const [loadingById, setLoadingById] = useState({});
  const [selectedMap, setSelectedMap] = useState("map1");

  // Calculate real KPI values from Stage of Extraction data
  const mergedKpis = useMemo(() => {
    const stageData = dataById["stageExtraction"] || [];
    if (stageData.length === 0) {
      return {
        safe: 0,
        semiCritical: 0,
        critical: 0,
        overExploited: 0,
        saline: 0,
        total: 0,
      };
    }

    const safe = stageData.filter((row) => {
      const val = parseFloat(row["Stage of Extraction Total"]);
      return val > 0 && val < 70;
    }).length;

    const semiCritical = stageData.filter((row) => {
      const val = parseFloat(row["Stage of Extraction Total"]);
      return val >= 70 && val < 90;
    }).length;

    const critical = stageData.filter((row) => {
      const val = parseFloat(row["Stage of Extraction Total"]);
      return val >= 90 && val < 100;
    }).length;

    const overExploited = stageData.filter((row) => {
      const val = parseFloat(row["Stage of Extraction Total"]);
      return val >= 100;
    }).length;

    // For now, using a placeholder for saline (you can update this with actual saline data if available)
    const saline = Math.floor(stageData.length * 0.05); // Assuming 5% are saline areas

    const total = safe + semiCritical + critical + overExploited + saline;

    return { safe, semiCritical, critical, overExploited, saline, total };
  }, [dataById]);

  // Configure KPI sources (place your CSVs under public/Dashboard_CSV)
  const kpiConfigs = useMemo(
    () => [
      {
        id: "annualResources",
        title: "Annual Extractable Ground Water Resources (BCM)",
        tone: "emerald",
        csv: "/Dashboard_CSV/ANN_GRND_WTR_EXT_RSC_2024-2025.csv",
      },
      {
        id: "extractionAll",
        title: "Ground Water Extraction for all uses (BCM)",
        tone: "amber",
        csv: "/Dashboard_CSV/GRND_WTR_EXT_INDIA_2024-2025.csv",
      },
      {
        id: "rainfall",
        title: "Rainfall (mm)",
        tone: "orange",
        csv: "/Dashboard_CSV/RAINFALL(MM)_2024-2025.csv",
      },
      {
        id: "recharge",
        title: "Ground Water Recharge (BCM)",
        tone: "red",
        csv: "/Dashboard_CSV/GRND_WTR_REC_INDIA_2024-2025.csv",
      },
      {
        id: "naturalDischarge",
        title: "Natural Discharges (BCM)",
        tone: "sky",
        csv: "/Dashboard_CSV/NAT_DIS_2024-2025.csv",
      },
    ],
    []
  );

  // Load a CSV and store rows
  const loadCsv = (path, id) => {
    setLoadingById((s) => ({ ...s, [id]: true }));
    Papa.parse(path, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (res) => {
        // PapaParse will rename duplicate headers automatically and also emits a warning.
        // To make keys deterministic and avoid ambiguous properties downstream,
        // rebuild rows using the meta.fields array and append stable suffixes to duplicates.
        const rawRows = Array.isArray(res.data) ? res.data : [];
        const fields =
          res && res.meta && Array.isArray(res.meta.fields)
            ? res.meta.fields
            : [];
        if (fields.length === 0) {
          setDataById((s) => ({ ...s, [id]: rawRows }));
          setLoadingById((s) => ({ ...s, [id]: false }));
          return;
        }

        // Create deterministic new field names: first occurrence keeps name, duplicates get _1, _2, ...
        const counts = {};
        const newFieldNames = fields.map((f) => {
          const name = String(f || "").trim();
          counts[name] = (counts[name] || 0) + 1;
          return counts[name] === 1 ? name : `${name}_${counts[name] - 1}`;
        });

        // Rebuild rows with the deterministic field names in the original column order
        const rows = rawRows.map((r) => {
          const obj = {};
          fields.forEach((orig, idx) => {
            const newKey = newFieldNames[idx] || `col_${idx}`;
            // Use the value as parsed by Papa; orig may already have been renamed by Papa
            obj[newKey] =
              r[fields[idx]] !== undefined ? r[fields[idx]] : r[newKey];
          });
          return obj;
        });

        setDataById((s) => ({ ...s, [id]: rows }));
        setLoadingById((s) => ({ ...s, [id]: false }));
      },
      error: () => setLoadingById((s) => ({ ...s, [id]: false })),
    });
  };

  // Load all KPI CSVs on mount
  useEffect(() => {
    kpiConfigs.forEach((k) => loadCsv(k.csv, k.id));
    // Also load Stage of Extraction for merged KPI (OVRL) — URL-encode the filename
    const stageFile = "Stage of Extraction (%_OVRL)_2024-25.csv";
    const stagePath = `/Dashboard_CSV/${encodeURIComponent(stageFile)}`;
    loadCsv(stagePath, "stageExtraction");

    // Try loading the INGRES flat CSV (headers include STATE,DISTRICT,RR_Tot,AGR_Tot,AER_Tot)
    // Try multiple common locations so local dev setups can find it.
    loadCsv("/header_flat_csv/INGRES_2024-25.csv", "ingres2024");
    loadCsv("/Dashboard_CSV/INGRES_2024-25.csv", "ingres2024_alternate");
    loadCsv("/INGRES_2024-25.csv", "ingres2024_root");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Helper to compute a value from rows
  // Requirement: take the cell value at the last row of the last column
  const computeValueFromRows = (rows) => {
    if (!rows || rows.length === 0) return "--";
    const lastRow = rows[rows.length - 1];
    const keys = Object.keys(lastRow);
    if (keys.length === 0) return "--";
    const lastKey = keys[keys.length - 1];
    return lastRow[lastKey];
  };

  // Format a number to first N significant integer digits for compact display
  const formatCompact = (value, digits = 4) => {
    if (value === "--" || value == null || Number.isNaN(value)) return "--";
    const absVal = Math.abs(value);
    const intStr = Math.trunc(absVal).toString();
    if (intStr.length <= digits) return intStr;
    return intStr.slice(0, digits);
  };

  // Build KPI objects with live values
  const kpis = useMemo(
    () =>
      kpiConfigs.map((k) => ({
        key: k.id,
        title: k.title,
        value: computeValueFromRows(dataById[k.id]),
        tone: k.tone,
        description: `${k.title} derived from ${k.csv.split("/").pop()}.`,
        formula:
          "Value = Sum of first numeric column (placeholder). Replace with your own logic.",
      })),
    [dataById, kpiConfigs]
  );

  // Use the Stage of Extraction dataset inside merged modal
  const mergedDataset = useMemo(
    () => dataById["stageExtraction"] || [],
    [dataById]
  );

  // Compute OVRL from Stage of Extraction CSV for merged KPI "Total" display
  // Pie chart data for groundwater categories
  const pieChartData = useMemo(
    () => [
      {
        name: t.status.safe,
        value: mergedKpis.safe,
        color: "#10b981",
        percentage:
          mergedKpis.total > 0
            ? ((mergedKpis.safe / mergedKpis.total) * 100).toFixed(1)
            : 0,
      },
      {
        name: t.status.semiCritical,
        value: mergedKpis.semiCritical,
        color: "#f59e0b",
        percentage:
          mergedKpis.total > 0
            ? ((mergedKpis.semiCritical / mergedKpis.total) * 100).toFixed(1)
            : 0,
      },
      {
        name: t.status.critical,
        value: mergedKpis.critical,
        color: "#f97316",
        percentage:
          mergedKpis.total > 0
            ? ((mergedKpis.critical / mergedKpis.total) * 100).toFixed(1)
            : 0,
      },
      {
        name: t.status.overExploited,
        value: mergedKpis.overExploited,
        color: "#ef4444",
        percentage:
          mergedKpis.total > 0
            ? ((mergedKpis.overExploited / mergedKpis.total) * 100).toFixed(1)
            : 0,
      },
      {
        name: t.status.saline,
        value: mergedKpis.saline,
        color: "#8b5cf6",
        percentage:
          mergedKpis.total > 0
            ? ((mergedKpis.saline / mergedKpis.total) * 100).toFixed(1)
            : 0,
      },
    ],
    [mergedKpis, t.status]
  );

  return (
    <div className="min-h-screen px-4 py-6 pt-24 bg-[#030714] relative">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      {/* Main content container */}
      <div className="relative z-10">
        {/* Charts Grid - Pie Chart and Dual Axis Chart side by side */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          {/* Groundwater Categories Pie Chart */}
          <div
            className="lg:col-span-1 rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-5 cursor-pointer hover:bg-slate-800/60 hover:border-cyan-400/40 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25"
            onClick={() => setMergedOpen(true)}
          >
            <div className="flex flex-col gap-1 mb-5">
              <h2 className="text-lg font-semibold text-slate-200">
                {t.dashboard.extractionCategories}
              </h2>
              <p className="text-sm text-slate-400">
                {t.dashboard.total}: {formatCompact(mergedKpis.total)} {t.dashboard.areas}
              </p>
            </div>

            <div className="flex flex-col gap-3">
              {/* Pie Chart */}
              <div className="w-full h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius="25%"
                      outerRadius="90%"
                      paddingAngle={1}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "1px solid rgba(255, 255, 255, 0.1)",
                        borderRadius: "6px",
                        color: "#ffffff",
                        fontSize: "12px",
                      }}
                      labelStyle={{
                        color: "#ffffff",
                      }}
                      itemStyle={{
                        color: "#ffffff",
                      }}
                      formatter={(value, name) => [
                        `${value} areas (${
                          pieChartData.find((d) => d.name === name)?.percentage
                        }%)`,
                        name,
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Statistics Summary */}
              <div className="space-y-3">
                {pieChartData.map((category) => (
                  <div
                    key={category.name}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors min-h-[80px] border border-white/10"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-4 h-4 rounded-full flex-shrink-0"
                        style={{ backgroundColor: category.color }}
                      />
                      <span className="text-slate-200 text-base font-medium">
                        {category.name}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-slate-100 font-bold text-2xl">
                        {category.value.toLocaleString()}
                      </p>
                      <p className="text-sm text-slate-400">
                        {category.percentage}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Dual Axis Chart */}
          <div className="lg:col-span-2">
            <DualAxisChart data={mergedDataset} />
          </div>
        </div>

        {/* Five individual KPI cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-8">
          {kpis.map((k) => (
            <button
              key={k.key}
              onClick={() => setKpiOpen(k.key)}
              className="text-left rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 hover:bg-slate-800/60 hover:border-cyan-400/40 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 min-h-[120px] flex flex-col justify-center group"
            >
              <p className="text-lg text-slate-300 mb-3 leading-relaxed font-medium">
                {k.title}
              </p>
              <p className={`text-3xl font-bold text-slate-100`}>
                {loadingById[k.key] ? "…" : formatCompact(k.value)}
              </p>
            </button>
          ))}
        </div>

        <div className="grid gap-4">
          <DataSummary />
          {/* Map selector buttons */}
          <div className="flex items-center gap-3 mb-3">
            <button
              onClick={() => setSelectedMap("map1")}
              className={`px-4 py-2 rounded-xl border transition-all duration-300 ${
                selectedMap === "map1"
                  ? "bg-cyan-600/80 backdrop-blur-xl text-white border-cyan-400/50 shadow-lg shadow-cyan-500/25"
                  : "bg-slate-800/60 backdrop-blur-xl text-slate-200 border-slate-600/50 hover:border-cyan-500/30 hover:bg-slate-700/60"
              }`}
            >
              Stage of Extraction
            </button>
            <button
              onClick={() => setSelectedMap("map2")}
              className={`px-4 py-2 rounded-xl border transition-all duration-300 ${
                selectedMap === "map2"
                  ? "bg-cyan-600/80 backdrop-blur-xl text-white border-cyan-400/50 shadow-lg shadow-cyan-500/25"
                  : "bg-slate-800/60 backdrop-blur-xl text-slate-200 border-slate-600/50 hover:border-cyan-500/30 hover:bg-slate-700/60"
              }`}
            >
              Annual Rainfall
            </button>
            <button
              onClick={() => setSelectedMap("map3")}
              className={`px-4 py-2 rounded-xl border transition-all duration-300 ${
                selectedMap === "map3"
                  ? "bg-cyan-600/80 backdrop-blur-xl text-white border-cyan-400/50 shadow-lg shadow-cyan-500/25"
                  : "bg-slate-800/60 backdrop-blur-xl text-slate-200 border-slate-600/50 hover:border-cyan-500/30 hover:bg-slate-700/60"
              }`}
            >
              Annual Recharge
            </button>
            <button
              onClick={() => setSelectedMap("map4")}
              className={`px-4 py-2 rounded-xl border transition-all duration-300 ${
                selectedMap === "map4"
                  ? "bg-cyan-600/80 backdrop-blur-xl text-white border-cyan-400/50 shadow-lg shadow-cyan-500/25"
                  : "bg-slate-800/60 backdrop-blur-xl text-slate-200 border-slate-600/50 hover:border-cyan-500/30 hover:bg-slate-700/60"
              }`}
            >
              Annual Extractable
            </button>
          </div>
          {/* Combine any successful INGRES loads (we try multiple locations during boot) */}
          {(!dataById["ingres2024"] || dataById["ingres2024"].length === 0) &&
            (!dataById["ingres2024_alternate"] ||
              dataById["ingres2024_alternate"].length === 0) &&
            (!dataById["ingres2024_root"] ||
              dataById["ingres2024_root"].length === 0) && (
              <div className="text-sm text-amber-300 mb-3">
                INGRES flat CSV not loaded (maps 2-4 rely on it). Place
                `INGRES_2024-25.csv` under `public/header_flat_csv` or
                `public/Dashboard_CSV`.
              </div>
            )}

          {/* prefer the first non-empty load, or merge if multiple were loaded */}
          {(() => {
            const a = dataById["ingres2024"] || [];
            const b = dataById["ingres2024_alternate"] || [];
            const c = dataById["ingres2024_root"] || [];
            const merged = [];
            // merge by appending; avoid duplicates by STATE||DISTRICT key when possible
            const seen = new Set();
            [...a, ...b, ...c].forEach((r) => {
              const key = `${r.STATE || ""}||${r.DISTRICT || ""}`;
              if (!seen.has(key)) {
                seen.add(key);
                merged.push(r);
              }
            });
            return (
              <GroundwaterMap
                mapId={selectedMap}
                stageData={mergedDataset}
                ingresData={merged}
              />
            );
          })()}
          {/* Legend for Map1 (OVRL categories) */}
          {selectedMap === "map1" && (
            <div className="mt-4 bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10">
              <p className="text-sm font-semibold text-slate-100 mb-3">Map Legend</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                  <span
                    className="w-4 h-4 rounded-full shadow-lg shadow-emerald-500/30"
                    style={{ backgroundColor: "#10b981" }}
                  ></span>
                  <span className="text-sm text-slate-200 font-medium">Safe (&lt;70%)</span>
                </div>
                <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                  <span
                    className="w-4 h-4 rounded-full shadow-lg shadow-amber-500/30"
                    style={{ backgroundColor: "#f59e0b" }}
                  ></span>
                  <span className="text-sm text-slate-200 font-medium">
                    Semi-Critical (70-90%)
                  </span>
                </div>
                <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                  <span
                    className="w-4 h-4 rounded-full shadow-lg shadow-orange-500/30"
                    style={{ backgroundColor: "#f97316" }}
                  ></span>
                  <span className="text-sm text-slate-200 font-medium">
                    Critical (90-100%)
                  </span>
                </div>
                <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                  <span
                    className="w-4 h-4 rounded-full shadow-lg shadow-red-500/30"
                    style={{ backgroundColor: "#ef4444" }}
                  ></span>
                  <span className="text-sm text-slate-200 font-medium">
                    Over-Exploited (≥100%)
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Merged KPI Modal */}
      <Modal
        open={mergedOpen}
        onClose={() => setMergedOpen(false)}
        title="Stage of Extraction Data (OVRL) - 2024-25"
      >
        <div className="grid gap-6">
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10">
            <p className="text-sm text-slate-200 leading-relaxed">
              This dataset shows the Stage of Extraction (%) for groundwater
              across different states and districts in India. The data indicates
              the percentage of groundwater extracted compared to the total
              extractable groundwater resources.
            </p>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="rounded-xl bg-emerald-800 backdrop-blur-sm border border-emerald-500 p-4 text-center hover:bg-emerald-700 hover:border-emerald-400 transition-all duration-300 shadow-lg hover:shadow-emerald-500/20">
                <p className="text-xs text-emerald-300 font-medium">Safe (&lt; 70%)</p>
                <p className="text-xl font-bold text-emerald-100 mt-2">
                  {
                    mergedDataset.filter(
                      (row) => parseFloat(row["Stage of Extraction Total"]) < 70
                    ).length
                  }
                </p>
              </div>
              <div className="rounded-xl bg-yellow-700 backdrop-blur-sm border border-yellow-500 p-4 text-center hover:bg-yellow-600 hover:border-yellow-400 transition-all duration-300 shadow-lg hover:shadow-yellow-500/20">
                <p className="text-xs text-yellow-200 font-medium">Semi-Critical (70-90%)</p>
                <p className="text-xl font-bold text-yellow-50 mt-2">
                  {
                    mergedDataset.filter((row) => {
                      const val = parseFloat(row["Stage of Extraction Total"]);
                      return val >= 70 && val < 90;
                    }).length
                  }
                </p>
              </div>
              <div className="rounded-xl bg-orange-800 backdrop-blur-sm border border-orange-500 p-4 text-center hover:bg-orange-700 hover:border-orange-400 transition-all duration-300 shadow-lg hover:shadow-orange-500/20">
                <p className="text-xs text-orange-300 font-medium">Critical (90-100%)</p>
                <p className="text-xl font-bold text-orange-100 mt-2">
                  {
                    mergedDataset.filter((row) => {
                      const val = parseFloat(row["Stage of Extraction Total"]);
                      return val >= 90 && val < 100;
                    }).length
                  }
                </p>
              </div>
              <div className="rounded-xl bg-red-900 backdrop-blur-sm border border-red-600 p-4 text-center hover:bg-red-800 hover:border-red-500 transition-all duration-300 shadow-lg hover:shadow-red-600/20">
                <p className="text-xs text-red-300 font-medium">Over-Exploited (≥ 100%)</p>
                <p className="text-xl font-bold text-red-100 mt-2">
                  {
                    mergedDataset.filter(
                      (row) =>
                        parseFloat(row["Stage of Extraction Total"]) >= 100
                    ).length
                  }
                </p>
              </div>
            </div>
          </div>
          <div className="overflow-y-auto rounded-xl border border-cyan-500/20 bg-slate-900/20 backdrop-blur-sm max-h-[60vh] shadow-lg glass-scrollbar">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-800/40 backdrop-blur-sm text-slate-200 sticky top-0 border-b border-cyan-500/20">
                <tr>
                  <th className="px-3 py-2 text-left">S.No</th>
                  <th className="px-3 py-2 text-left">State</th>
                  <th className="px-3 py-2 text-left">District</th>
                  <th className="px-3 py-2 text-right">
                    Annual Extractable Resource (ham)
                  </th>
                  <th className="px-3 py-2 text-right">
                    Ground Water Extraction (ha.m)
                  </th>
                  <th className="px-3 py-2 text-right">
                    Stage of Extraction (%)
                  </th>
                </tr>
              </thead>
              <tbody>
                {mergedDataset.map((row, idx) => {
                  const extractionPct = parseFloat(
                    row["Stage of Extraction Total"]
                  );
                  let rowClass = "odd:bg-slate-800/20 hover:bg-slate-700/30 transition-colors duration-200";
                  let statusClass = "text-slate-300";

                  if (extractionPct >= 100) {
                    rowClass += " bg-red-900/20 hover:bg-red-800/30";
                    statusClass = "text-red-400 font-medium";
                  } else if (extractionPct >= 90) {
                    rowClass += " bg-orange-900/20 hover:bg-orange-800/30";
                    statusClass = "text-orange-400 font-medium";
                  } else if (extractionPct >= 70) {
                    rowClass += " bg-amber-900/20 hover:bg-amber-800/30";
                    statusClass = "text-amber-400 font-medium";
                  } else {
                    statusClass = "text-emerald-400";
                  }

                  return (
                    <tr key={idx} className={rowClass}>
                      <td className="px-3 py-2 text-slate-400">
                        {row["S.No"]}
                      </td>
                      <td className="px-3 py-2 text-slate-200">
                        {row["STATE"]}
                      </td>
                      <td className="px-3 py-2 text-slate-200">
                        {row["DISTRICT"]}
                      </td>
                      <td className="px-3 py-2 text-right text-slate-300">
                        {parseFloat(
                          row[
                            "Annual Extractable Ground water Resource (ham)Total"
                          ]
                        ).toLocaleString()}
                      </td>
                      <td className="px-3 py-2 text-right text-slate-300">
                        {parseFloat(
                          row[
                            "Ground Water Extraction for all uses (ha.m) Total"
                          ]
                        ).toLocaleString()}
                      </td>
                      <td className={`px-3 py-2 text-right ${statusClass}`}>
                        {extractionPct ? extractionPct.toFixed(2) : "0.00"}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10">
            <p className="text-sm font-bold text-slate-100 mb-4">
              Classification Categories
            </p>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-slate-200">
              <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                <span className="w-4 h-4 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/30"></span>
                <span>
                  <strong className="text-emerald-400">Safe:</strong> &lt; 70% extraction
                </span>
              </li>
              <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                <span className="w-4 h-4 rounded-full bg-amber-500 shadow-lg shadow-amber-500/30"></span>
                <span>
                  <strong className="text-amber-400">Semi-Critical:</strong> 70-90% extraction
                </span>
              </li>
              <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                <span className="w-4 h-4 rounded-full bg-orange-500 shadow-lg shadow-orange-500/30"></span>
                <span>
                  <strong className="text-orange-400">Critical:</strong> 90-100% extraction
                </span>
              </li>
              <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700/30 transition-colors duration-200">
                <span className="w-4 h-4 rounded-full bg-red-500 shadow-lg shadow-red-500/30"></span>
                <span>
                  <strong className="text-red-400">Over-Exploited:</strong> ≥ 100% extraction
                </span>
              </li>
            </ul>
            <div className="mt-4 p-3 bg-slate-700/30 rounded-lg border border-cyan-500/10">
              <p className="text-xs text-slate-300 leading-relaxed">
                <strong className="text-cyan-400">Note:</strong> Stage of Extraction indicates the
                percentage of groundwater extracted compared to total extractable
                resources. Values over 100% indicate over-exploitation of
                groundwater resources.
              </p>
            </div>
          </div>
        </div>
      </Modal>

      {/* Individual KPI Modals */}
      {kpis.map((k) => (
        <Modal
          key={k.key}
          open={kpiOpen === k.key}
          onClose={() => setKpiOpen(null)}
          title={`${k.title} Details`}
        >
          <div className="grid gap-6">
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10">
              <p className="text-sm text-slate-200 leading-relaxed">{k.description}</p>
            </div>
            <div className="overflow-y-auto rounded-xl border border-cyan-500/20 bg-slate-900/20 backdrop-blur-sm max-h-[70vh] shadow-lg glass-scrollbar">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-800/40 backdrop-blur-sm text-slate-200 sticky top-0 border-b border-cyan-500/20">
                  <tr>
                    {dataById[k.key] && dataById[k.key].length > 0
                      ? Object.keys(dataById[k.key][0]).map((col) => (
                          <th key={col} className="px-3 py-2 text-left font-medium">
                            {col}
                          </th>
                        ))
                      : null}
                  </tr>
                </thead>
                <tbody>
                  {(dataById[k.key] || []).map((row, idx) => (
                    <tr key={idx} className="odd:bg-slate-800/20 hover:bg-slate-700/30 transition-colors duration-200">
                      {Object.keys(row).map((col) => (
                        <td key={col} className="px-3 py-2 whitespace-nowrap text-slate-300">
                          {String(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-cyan-500/10">
              <p className="text-sm font-bold text-slate-100 mb-3">
                Formula
              </p>
              <p className="text-sm text-slate-200 font-mono bg-slate-700/40 p-3 rounded-lg border border-cyan-500/20">{k.formula}</p>
            </div>
          </div>
        </Modal>
      ))}
    </div>
  );
}
