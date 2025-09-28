import { NavLink } from "react-router-dom";
import LanguageSwitcher from "./LanguageSwitcher";
import { useI18n } from "../../i18n/I18nContext";

export default function Header() {
  const { t } = useI18n();
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-slate-900/20 backdrop-blur-xl border-b border-cyan-500/20 shadow-lg">
      {/* Animated gradient border */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"></div>

      {/* Glassmorphism overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-slate-900/10 via-blue-900/5 to-slate-900/10"></div>

      <div className="relative mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
        {/* Logo Section with Glow Effect */}
        <div className="flex items-center gap-3 group">
          <div className="relative">
            <div className="absolute inset-0 bg-cyan-500/30 rounded-full blur-md group-hover:bg-cyan-400/40 transition-colors duration-300"></div>
            <img
              src="/logo1.png"
              alt={t.brand}
              className="relative h-10 w-10 drop-shadow-lg transition-transform group-hover:scale-110 duration-300"
            />
          </div>
          <span className="font-bold text-lg bg-gradient-to-r from-cyan-300 to-teal-300 bg-clip-text text-transparent">
            {t.brand}
          </span>
        </div>

        {/* Navigation with Glassmorphism Links */}
        <nav className="hidden md:flex items-center gap-2">
          <NavLink
            to="/"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">{t.nav.home}</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>

          <NavLink
            to="/chat"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">{t.nav.chatbot}</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>

          <NavLink
            to="/dashboard"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">{t.nav.dashboard}</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>

          <NavLink
            to="/search"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">{t.nav.search}</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>

          <NavLink
            to="/historical"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">{t.nav.historical}</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>

          <NavLink
            to="/prediction"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">Predictions</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>

          <NavLink
            to="/help"
            className={({ isActive }) => `
							relative px-4 py-2 rounded-xl font-medium transition-all duration-300 group overflow-hidden
							${
                isActive
                  ? "text-cyan-300 bg-cyan-500/20 backdrop-blur-sm border border-cyan-500/30 shadow-lg shadow-cyan-500/25"
                  : "text-slate-300 hover:text-cyan-300 hover:bg-slate-800/30 hover:backdrop-blur-sm hover:border hover:border-cyan-500/20"
              }
						`}
          >
            {({ isActive }) => (
              <>
                <span className="relative z-10">{t.nav.help}</span>
                {!isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                )}
              </>
            )}
          </NavLink>
        </nav>

        {/* Language Switcher with Enhanced Styling */}
        <div className="relative">
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
}
