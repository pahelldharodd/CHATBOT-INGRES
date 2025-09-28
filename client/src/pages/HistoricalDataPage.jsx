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
    <div className="min-h-screen bg-[#030714] relative flex flex-col">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,_#1a365d_0%,_transparent_50%)] animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_100%_100%,_#0d9488_0%,_transparent_50%)] animate-pulse [animation-delay:1s]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_#1e40af_0%,_transparent_50%)] animate-pulse [animation-delay:2s]"></div>

      {/* Header */}
      <div className="relative z-10 pt-20 pb-6">
        <div className="mx-auto max-w-4xl px-4">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-slate-100 mb-2 text-glow">
              Historical Data Assistant
            </h1>
            <p className="text-slate-300">
              Ask questions about historical groundwater documents and get AI-powered insights
            </p>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 relative z-10 flex flex-col max-w-4xl mx-auto w-full px-4 pb-6">
        {/* Chat Messages Area */}
        <div className="flex-1 rounded-2xl border border-cyan-500/20 bg-slate-900/20 backdrop-blur-xl shadow-lg mb-4 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-[400px] glass-scrollbar">
            {history.length === 0 && !loading && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-cyan-500/20 to-teal-500/20 flex items-center justify-center">
                    <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-slate-200 mb-2">Ready to help!</h3>
                  <p className="text-sm text-slate-400 max-w-md">
                    Ask me anything about historical groundwater data, assessments, or documents. 
                    I'll search through the knowledge base to provide accurate answers.
                  </p>
                </div>
              </div>
            )}

            {history.map((item, idx) => (
              <div key={idx} className="space-y-4">
                {/* User Message */}
                <div className="flex justify-end">
                  <div className="max-w-2xl group">
                    <div className="bg-gradient-to-r from-cyan-600/90 to-teal-600/90 backdrop-blur-xl border border-cyan-400/30 rounded-2xl rounded-br-md px-6 py-4 text-white shadow-lg">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mt-0.5">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium leading-relaxed">{item.question}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Assistant Message */}
                <div className="flex justify-start">
                  <div className="max-w-3xl group">
                    <div className="bg-slate-800/60 backdrop-blur-xl border border-slate-600/30 rounded-2xl rounded-bl-md px-6 py-4 text-slate-100 shadow-lg">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500/30 to-teal-500/30 flex items-center justify-center mt-0.5">
                          <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          {item.pending ? (
                            <div className="flex items-center gap-2">
                              <div className="flex gap-1">
                                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.1s]"></div>
                                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                              </div>
                              <span className="text-sm text-slate-400">Analyzing documents...</span>
                            </div>
                          ) : (
                            <>
                              <div className="prose prose-sm max-w-none text-slate-200 leading-relaxed">
                                <div className="whitespace-pre-wrap">{item.answer}</div>
                              </div>
                              {item.sources?.length > 0 && (
                                <div className="mt-4 pt-3 border-t border-slate-600/30">
                                  <div className="flex items-center gap-2 mb-2">
                                    <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    <span className="text-sm font-medium text-cyan-400">Sources</span>
                                  </div>
                                  <div className="space-y-2">
                                    {item.sources.map((s, sourceIdx) => (
                                      <div key={s.id || `${idx}-${sourceIdx}`} className="bg-slate-700/40 rounded-lg p-3 border border-slate-600/30">
                                        <div className="flex items-start gap-2">
                                          <div className="flex-shrink-0 w-6 h-6 bg-cyan-500/20 rounded flex items-center justify-center mt-0.5">
                                            <span className="text-xs font-bold text-cyan-400">{sourceIdx + 1}</span>
                                          </div>
                                          <div className="text-sm text-slate-300">
                                            {s.label && <span className="font-medium text-cyan-300">[{s.label}] </span>}
                                            <span>{s.source || "Unknown"}</span>
                                            {s.page && <span className="text-slate-400"> • page {s.page}</span>}
                                          </div>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {loading && !history.length && (
              <div className="flex items-center justify-center h-full">
                <div className="bg-slate-800/60 backdrop-blur-xl border border-slate-600/30 rounded-2xl px-6 py-4 shadow-lg">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.1s]"></div>
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                    </div>
                    <span className="text-slate-200">Processing your question...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Suggested Questions */}
          {history.length === 0 && !loading && (
            <div className="border-t border-slate-600/30 p-6 bg-slate-800/20">
              <div className="mb-3">
                <h4 className="text-sm font-medium text-slate-200 mb-3">💡 Try asking:</h4>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  "What are the key findings in the historical assessments?",
                  "How has groundwater extraction changed over time?",
                  "What methods were used in past assessments?",
                  "What are the main challenges mentioned in the documents?"
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuestion(suggestion)}
                    className="text-left p-3 rounded-lg bg-slate-700/30 border border-slate-600/30 hover:bg-slate-700/50 hover:border-cyan-500/30 transition-all duration-200 text-sm text-slate-300 hover:text-slate-200"
                  >
                    "{suggestion}"
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/40 backdrop-blur-xl shadow-lg p-4">
          <form onSubmit={askHistorical} className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about historical groundwater documents..."
                disabled={loading}
                className="w-full rounded-xl border border-cyan-500/30 bg-slate-800/60 backdrop-blur-xl px-4 py-3 pr-12 text-slate-100 placeholder-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 transition-all disabled:opacity-50"
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="group relative px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600/90 to-teal-600/90 backdrop-blur-xl border border-cyan-400/30 text-white font-semibold hover:from-cyan-500/90 hover:to-teal-500/90 hover:border-cyan-300/40 hover:shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <span className="relative flex items-center gap-2">
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Send
                  </>
                )}
              </span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
