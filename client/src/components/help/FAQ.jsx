import { useI18n } from "../../i18n/I18nContext";

export default function FAQ() {
  const { t } = useI18n();
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 text-slate-100 shadow-lg">
      <h3 className="font-semibold mb-4 text-cyan-300 text-lg">{t.help.faq}</h3>
      <ul className="list-disc pl-5 text-sm text-slate-300 space-y-1">
        {t.help.faqItems.map((q) => (
          <li key={q}>{q}</li>
        ))}
      </ul>
    </div>
  );
}
