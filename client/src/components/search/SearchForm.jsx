import { useI18n } from "../../i18n/I18nContext";

export default function SearchForm({
  regionOptions = [],
  yearOptions = [],
  region,
  setRegion,
  year,
  setYear,
  status,
  setStatus,
  district,
  setDistrict,
  districtOptions = [],
  showFresh = true,
  setShowFresh = () => {},
  showSaline = true,
  setShowSaline = () => {},
}) {
  const { t } = useI18n();
  return (
    <form
      className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 grid gap-4 shadow-lg"
      onSubmit={(e) => {
        e.preventDefault();
      }}
    >
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl text-slate-100 rounded-xl px-4 py-3 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
        >
          <option value="">{t.search.region}</option>
          {regionOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        {/* year */}
        <select
          value={year}
          onChange={(e) => setYear(e.target.value)}
          className="border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl text-slate-100 rounded-xl px-4 py-3 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
        >
          <option value="">{t.search.year}</option>
          {yearOptions.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>

        {/* district shows only when a region is chosen */}
        {region && (
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl text-slate-100 rounded-xl px-4 py-3 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
          >
            <option value="">All districts</option>
            {districtOptions.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        )}

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl text-slate-100 rounded-xl px-4 py-3 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
        >
          <option value="">{t.search.status}</option>
          <option value="safe">{t.status.safe}</option>
          <option value="semiCritical">{t.status.semiCritical}</option>
          <option value="critical">{t.status.critical}</option>
          <option value="overExploited">{t.status.overExploited}</option>
        </select>
      </div>

      <div className="flex items-center gap-6">
        <label className="flex items-center gap-3 text-sm cursor-pointer group">
          <input
            type="checkbox"
            checked={showFresh}
            onChange={(e) => setShowFresh(e.target.checked)}
            className="w-4 h-4 rounded border-cyan-500/30 text-cyan-500 focus:ring-2 focus:ring-cyan-500/50 bg-slate-700/50 transition-all duration-200"
          />
          <span className="text-slate-200 group-hover:text-cyan-300 transition-colors duration-200 font-medium">Fresh</span>
        </label>
        <label className="flex items-center gap-3 text-sm cursor-pointer group">
          <input
            type="checkbox"
            checked={showSaline}
            onChange={(e) => setShowSaline(e.target.checked)}
            className="w-4 h-4 rounded border-cyan-500/30 text-cyan-500 focus:ring-2 focus:ring-cyan-500/50 bg-slate-700/50 transition-all duration-200"
          />
          <span className="text-slate-200 group-hover:text-cyan-300 transition-colors duration-200 font-medium">Saline</span>
        </label>
      </div>

      <button
        type="submit"
        className="self-start group relative px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600/90 to-teal-600/90 backdrop-blur-xl border border-cyan-400/30 text-white font-semibold hover:from-cyan-500/90 hover:to-teal-500/90 hover:border-cyan-300/40 hover:shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <span className="relative flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {t.search.searchBtn}
        </span>
      </button>
    </form>
  );
}
