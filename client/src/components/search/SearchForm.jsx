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

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showFresh}
            onChange={(e) => setShowFresh(e.target.checked)}
          />
          <span className="ml-1">Fresh</span>
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showSaline}
            onChange={(e) => setShowSaline(e.target.checked)}
          />
          <span className="ml-1">Saline</span>
        </label>
      </div>

      <button
        type="submit"
        className="self-start rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-500"
      >
        {t.search.searchBtn}
      </button>
    </form>
  );
}
