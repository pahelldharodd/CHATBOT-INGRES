import { useI18n } from '../i18n/I18nContext'

export default function Home() {
	const { t } = useI18n()
	return (
		<section className="mx-auto max-w-6xl px-4 py-12">
			<div className="text-center">
				<img src="/logo1.png" alt={t.brand} className="h-18 w-18 mx-auto mb-4" />
				<h1 className="text-4xl font-bold mb-2 text-white">{t.home.welcome}</h1>
				<p className="text-lg text-slate-300 mb-8">{t.home.desc}</p>
				<div className="flex flex-wrap gap-4 justify-center">
					<a href="/chat" className="px-5 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-500">{t.home.startChat}</a>
					<a href="/dashboard" className="px-5 py-3 bg-emerald-600 text-white rounded-md hover:bg-emerald-500">{t.home.exploreData}</a>
					<a href="/search" className="px-5 py-3 bg-slate-800 text-white rounded-md hover:bg-slate-700">{t.home.searchData}</a>
				</div>
			</div>
		</section>
	)
}
