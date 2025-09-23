import { useI18n } from '../../i18n/I18nContext'

export default function Footer() {
	const { t } = useI18n()
	return (
		<footer className="border-t border-white/10 bg-black/60 backdrop-blur">
			<div className="mx-auto max-w-6xl px-4 py-6 text-sm text-slate-300 flex flex-col md:flex-row items-center justify-between gap-4">
				<p>© {new Date().getFullYear()} IN-GRES. All rights reserved.</p>
				<nav className="flex gap-4">
					<a href="#" className="hover:text-white">{t.footer.privacy}</a>
					<a href="#" className="hover:text-white">{t.footer.contact}</a>
					<a href="#" className="hover:text-white">{t.footer.terms}</a>
				</nav>
			</div>
		</footer>
	)
}
