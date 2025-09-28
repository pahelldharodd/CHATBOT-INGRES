import { useI18n } from "../../i18n/I18nContext";

export default function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  return (
    <div className="relative group">
      <label className="inline-flex items-center gap-3 text-slate-300">
        <span className="sr-only">Language</span>
        <div className="text-lg filter drop-shadow-lg">🌐</div>
        <div className="relative">
          {/* Glassmorphism background */}
          <div className="absolute inset-0 bg-slate-800/30 backdrop-blur-sm rounded-xl border border-cyan-500/20 group-hover:border-cyan-400/40 transition-all duration-300"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/5 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>

          <select
            value={locale}
            onChange={(e) => setLocale(e.target.value)}
            className="relative bg-transparent text-slate-100 rounded-xl px-4 py-2 text-sm font-medium cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400/50 focus:border-cyan-400/50 appearance-none pr-8 min-w-[100px] transition-all duration-300"
            aria-label={locale === "EN" ? "Language" : "भाषा"}
          >
            <option value="EN" className="bg-slate-900 text-slate-100">
              English
            </option>
            <option value="HI" className="bg-slate-900 text-slate-100">
              हिंदी
            </option>
          </select>

          {/* Custom dropdown arrow */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
            <svg
              className="w-4 h-4 text-cyan-300 group-hover:text-cyan-200 transition-colors duration-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </label>
    </div>
  );
}
