import { useI18n } from "../../i18n/I18nContext";

export default function ContactSupport() {
  const { t } = useI18n();
  return (
    <form className="rounded-2xl border border-blue-500/20 bg-slate-900/40 backdrop-blur-xl p-6 grid gap-4 text-slate-100 shadow-lg">
      <h3 className="font-semibold mb-2 text-blue-300 text-lg">
        {t.help.contact}
      </h3>
      <input
        className="border border-blue-500/30 bg-slate-800/60 backdrop-blur-xl rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 transition-all"
        placeholder={t.help.emailPlaceholder}
      />
      <textarea
        className="border border-blue-500/30 bg-slate-800/60 backdrop-blur-xl rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 transition-all"
        placeholder={t.help.issuePlaceholder}
        rows="4"
      />
      <button className="self-start rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-3 hover:from-blue-500 hover:to-blue-400 transition-all duration-300 shadow-lg hover:shadow-blue-500/25">
        {t.help.sendBtn}
      </button>
    </form>
  );
}
