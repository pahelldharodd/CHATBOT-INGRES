export default function MessageBox({ role, text }) {
	const isUser = role === 'user'
	return (
		<div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
			<div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${isUser ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-100 border border-white/10'}`}>
				{text}
			</div>
		</div>
	)
}
