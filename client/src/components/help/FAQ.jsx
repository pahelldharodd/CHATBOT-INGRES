import { useI18n } from '../../i18n/I18nContext'

export default function FAQ() {
	const { t } = useI18n()
	return (
		<div className="rounded-lg border border-white/10 bg-slate-900 p-4 text-slate-100">
			<h3 className="font-medium mb-2">{t.help.faq}</h3>
			<ul className="list-disc pl-5 text-sm text-slate-300 space-y-1">
				{t.help.faqItems.map((q) => (
					<li key={q}>{q}</li>
				))}
			</ul>
		</div>
	)
}
