import { useI18n } from "../../i18n/I18nContext";

export default function Tutorial() {
  const { t } = useI18n();
  return (
    <div className="rounded-2xl border border-teal-500/20 bg-slate-900/40 backdrop-blur-xl p-6 text-slate-100 shadow-lg">
      <h3 className="font-semibold mb-4 text-teal-300 text-lg">
        {t.help.tutorial}
      </h3>
      <ol className="list-decimal pl-5 text-sm text-slate-300 space-y-1">
        {t.help.tutorialSteps.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ol>
    </div>
  );
}
