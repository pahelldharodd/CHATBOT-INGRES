import { useI18n } from '../../i18n/I18nContext'

export default function ContactSupport() {
	const { t } = useI18n()
	return (
		<form className="rounded-lg border border-white/10 bg-slate-900 p-4 grid gap-3 text-slate-100">
			<h3 className="font-medium">{t.help.contact}</h3>
			<input className="border border-white/10 rounded px-3 py-2 bg-slate-800 text-slate-100 placeholder:text-slate-400" placeholder={t.help.emailPlaceholder} />
			<textarea className="border border-white/10 rounded px-3 py-2 bg-slate-800 text-slate-100 placeholder:text-slate-400" placeholder={t.help.issuePlaceholder} rows="4" />
			<button className="self-start rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-500">{t.help.sendBtn}</button>
		</form>
	)
}
