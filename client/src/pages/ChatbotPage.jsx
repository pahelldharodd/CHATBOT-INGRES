// import ChatWindow from '../components/chatbot/ChatWindow'
// import QuickReplies from '../components/chatbot/QuickReplies'

export default function ChatbotPage() {
	return (
		<div className="mx-auto max-w-5xl px-4 py-8 grid gap-6">
			{/* <ChatWindow />
			<QuickReplies /> */}
            <div className="w-full" style={{ height: '85vh' }}>
                <iframe
                    title="Gradio Chatbot"
                    src="/gradio"
                    className="w-full h-full border rounded"
                    allow="clipboard-read; clipboard-write;"
                />
            </div>
		</div>
	)
}
