import { NavLink } from 'react-router-dom'
import LanguageSwitcher from './LanguageSwitcher'
import { useI18n } from '../../i18n/I18nContext'

export default function Header() {
	const { t } = useI18n()
	return (
		<header className="border-b border-white/10 bg-black/60 backdrop-blur">
			<div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
				<div className="flex items-center gap-2">
					<img src="/logo1.png" alt={t.brand} className="h-8 w-8" />
					<span className="font-semibold">{t.brand}</span>
				</div>
				<nav className="hidden md:flex items-center gap-6">
					<NavLink to="/" className={({isActive}) => isActive ? 'text-blue-400' : 'text-slate-200'}>{t.nav.home}</NavLink>
					<NavLink to="/chat" className={({isActive}) => isActive ? 'text-blue-400' : 'text-slate-200'}>{t.nav.chatbot}</NavLink>
					<NavLink to="/dashboard" className={({isActive}) => isActive ? 'text-blue-400' : 'text-slate-200'}>{t.nav.dashboard}</NavLink>
					<NavLink to="/search" className={({isActive}) => isActive ? 'text-blue-400' : 'text-slate-200'}>{t.nav.search}</NavLink>
					<NavLink to="/historical" className={({isActive}) => isActive ? 'text-blue-400' : 'text-slate-200'}>{t.nav.historical}</NavLink>
					<NavLink to="/help" className={({isActive}) => isActive ? 'text-blue-400' : 'text-slate-200'}>{t.nav.help}</NavLink>
				</nav>
				<LanguageSwitcher />
			</div>
		</header>
	)
}
