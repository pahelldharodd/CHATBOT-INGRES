import ChatWindow from '../components/chatbot/ChatWindow'
import QuickReplies from '../components/chatbot/QuickReplies'

export default function ChatbotPage() {
	return (
		<div className="mx-auto max-w-5xl px-4 py-8 grid gap-6">
			<ChatWindow />
			<QuickReplies />
		</div>
	)
}
