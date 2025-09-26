import { useState } from 'react'
const API_BASE = 'http://localhost:7861'

export default function HistoricalDataPage() {
	const [question, setQuestion] = useState('')
	const [history, setHistory] = useState([])
	const [loading, setLoading] = useState(false)

	async function askHistorical(e) {
		e?.preventDefault?.()
		const trimmed = question.trim()
		if (!trimmed) return

		setQuestion('')
		setLoading(true)
		setHistory((prev) => [
			...prev,
			{ question: trimmed, answer: '', sources: [], pending: true }
		])

		try {
			const res = await fetch(`${API_BASE}/historical/ask`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ question: trimmed, top_k: 4 })
			})
			const data = await res.json().catch(() => ({}))
			if (!res.ok) {
				const detail = data?.detail || (typeof data === 'string' ? data : '')
				throw new Error(detail || `Request failed: ${res.status}`)
			}
			setHistory((prev) => {
				if (!prev.length) return prev
				const lastIndex = prev.length - 1
				const updated = [...prev]
				updated[lastIndex] = {
					...updated[lastIndex],
					answer: data.answer || 'No answer returned.',
					sources: Array.isArray(data.sources) ? data.sources : [],
					pending: false
				}
				return updated
			})
		} catch (err) {
			console.error(err)
			setHistory((prev) => {
				if (!prev.length) return prev
				const lastIndex = prev.length - 1
				const updated = [...prev]
				const msg = err?.message || 'Sorry, something went wrong fetching the historical answer.'
				updated[lastIndex] = {
					...updated[lastIndex],
					answer: msg,
					sources: [],
					pending: false
				}
				return updated
			})
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="mx-auto max-w-6xl px-4 py-8 grid gap-6">
			<div className="rounded-lg border border-gray-200 p-4">
				<h2 className="text-lg font-semibold mb-3">Ask about historical PDFs</h2>
				<form onSubmit={askHistorical} className="flex gap-2">
					<input
						type="text"
						value={question}
						onChange={(e) => setQuestion(e.target.value)}
						placeholder="Ask a question about historical documents..."
						className="flex-1 rounded-md border border-gray-300 px-3 py-2"
					/>
					<button
						type="submit"
						disabled={loading}
						className="rounded-md bg-blue-600 px-4 py-2 text-white disabled:opacity-60"
					>
						{loading ? 'Asking…' : 'Ask'}
					</button>
				</form>

				<div className="mt-6 space-y-6">
					{history.map((item, idx) => (
						<div key={idx} className="space-y-3">
							<div className="flex justify-end">
								<div className="max-w-xl rounded-lg bg-blue-600 px-4 py-2 text-white shadow">
									{item.question}
								</div>
							</div>
							<div className="flex justify-start">
								<div className="max-w-2xl rounded-lg bg-gray-50 px-4 py-3 text-gray-900 shadow">
									{item.pending ? (
										<div className="italic text-gray-500">Thinking…</div>
									) : (
										<>
											<div className="prose prose-sm max-w-none whitespace-pre-wrap">
												{item.answer}
											</div>
											{item.sources?.length > 0 && (
												<div className="mt-3 border-t border-gray-200 pt-2 text-sm text-gray-600">
													<div className="font-medium text-gray-700">Sources</div>
													<ul className="mt-1 space-y-1 list-disc pl-5">
														{item.sources.map((s, sourceIdx) => (
															<li key={s.id || `${idx}-${sourceIdx}`}>
																{s.label ? `[${s.label}] ` : ''}{s.source || 'Unknown'}{s.page ? ` • page ${s.page}` : ''}
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
						<div className="rounded-lg bg-gray-50 px-4 py-3 text-gray-600">Thinking…</div>
					)}
				</div>
			</div>
		</div>
	)
}
