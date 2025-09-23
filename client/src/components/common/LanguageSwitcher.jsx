import { useI18n } from '../../i18n/I18nContext'

export default function LanguageSwitcher() {
	const { locale, setLocale } = useI18n()
	return (
		<label className="inline-flex items-center gap-2 text-slate-200">
			<span className="sr-only">Language</span>
			<span className="text-xs">🌐</span>
			<select
				value={locale}
				onChange={(e) => setLocale(e.target.value)}
				className="border border-white/10 bg-slate-900 text-slate-100 rounded px-2 py-1 text-xs hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
				aria-label={locale === 'EN' ? 'Language' : 'भाषा'}
			>
				<option value="EN">English</option>
				<option value="HI">हिंदी</option>
			</select>
		</label>
	)
}
