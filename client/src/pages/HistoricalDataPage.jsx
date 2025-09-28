import { useState } from "react";
const API_BASE = "http://localhost:7861";

export default function HistoricalDataPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  async function askHistorical(e) {
    e?.preventDefault?.();
    const trimmed = question.trim();
    if (!trimmed) return;

    setQuestion("");
    setLoading(true);
    setHistory((prev) => [
      ...prev,
      { question: trimmed, answer: "", sources: [], pending: true },
    ]);

    try {
      const res = await fetch(`${API_BASE}/historical/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, top_k: 4 }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data?.detail || (typeof data === "string" ? data : "");
        throw new Error(detail || `Request failed: ${res.status}`);
      }
      setHistory((prev) => {
        if (!prev.length) return prev;
        const lastIndex = prev.length - 1;
        const updated = [...prev];
        updated[lastIndex] = {
          ...updated[lastIndex],
          answer: data.answer || "No answer returned.",
          sources: Array.isArray(data.sources) ? data.sources : [],
          pending: false,
        };
        return updated;
      });
    } catch (err) {
      console.error(err);
      setHistory((prev) => {
        if (!prev.length) return prev;
        const lastIndex = prev.length - 1;
        const updated = [...prev];
        const msg =
          err?.message ||
          "Sorry, something went wrong fetching the historical answer.";
        updated[lastIndex] = {
          ...updated[lastIndex],
          answer: msg,
          sources: [],
          pending: false,
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen pt-20 bg-[#030714] relative">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      <div className="mx-auto max-w-6xl px-4 py-8 grid gap-6 relative z-10">
        <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl p-6 shadow-lg">
          <h2 className="text-lg font-semibold mb-3">
            Ask about historical PDFs
          </h2>
          <form onSubmit={askHistorical} className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about historical documents..."
              className="flex-1 rounded-xl border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-gradient-to-r from-cyan-600 to-teal-600 px-6 py-3 text-white font-medium hover:from-cyan-500 hover:to-teal-500 disabled:opacity-60 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25"
            >
              {loading ? "Asking…" : "Ask"}
            </button>
          </form>

          <div className="mt-6 space-y-6">
            {history.map((item, idx) => (
              <div key={idx} className="space-y-3">
                <div className="flex justify-end">
                  <div className="max-w-xl rounded-2xl bg-cyan-600/80 backdrop-blur-xl border border-cyan-400/30 px-5 py-3 text-white shadow-lg">
                    {item.question}
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="max-w-2xl rounded-2xl bg-slate-800/60 backdrop-blur-xl border border-slate-600/30 px-5 py-4 text-slate-100 shadow-lg">
                    {item.pending ? (
                      <div className="italic text-gray-500">Thinking…</div>
                    ) : (
                      <>
                        <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                          {item.answer}
                        </div>
                        {item.sources?.length > 0 && (
                          <div className="mt-3 border-t border-gray-200 pt-2 text-sm text-gray-600">
                            <div className="font-medium text-gray-700">
                              Sources
                            </div>
                            <ul className="mt-1 space-y-1 list-disc pl-5">
                              {item.sources.map((s, sourceIdx) => (
                                <li key={s.id || `${idx}-${sourceIdx}`}>
                                  {s.label ? `[${s.label}] ` : ""}
                                  {s.source || "Unknown"}
                                  {s.page ? ` • page ${s.page}` : ""}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {loading && !history.length && (
              <div className="rounded-lg bg-gray-50 px-4 py-3 text-gray-600">
                Thinking…
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
