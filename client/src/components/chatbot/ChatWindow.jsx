import { useState } from 'react'
import MessageBox from './MessageBox'
import InputBox from './InputBox'
import { useI18n } from '../../i18n/I18nContext'

export default function ChatWindow() {
	const { t } = useI18n()
	const [messages, setMessages] = useState([
		{ id: 1, role: 'assistant', text: t.chat.greeting },
	])

	function handleSend(text) {
		if (!text.trim()) return
		setMessages((prev) => [...prev, { id: Date.now(), role: 'user', text }])
	}

	return (
		<div className="border border-white/10 rounded-lg bg-slate-900">
			<div className="h-80 overflow-y-auto p-4 space-y-3 glass-scrollbar">
				{messages.map((m) => (
					<MessageBox key={m.id} role={m.role} text={m.text} />
				))}
			</div>
			<div className="border-t border-white/10 p-3">
				<InputBox onSend={handleSend} />
			</div>
		</div>
	)
}
