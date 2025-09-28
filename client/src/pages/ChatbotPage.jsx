// import ChatWindow from '../components/chatbot/ChatWindow'
// import QuickReplies from '../components/chatbot/QuickReplies'

export default function ChatbotPage() {
  return (
    <div className="w-full min-h-screen bg-[#030714] pt-16">
      {/* <ChatWindow />
			<QuickReplies /> */}
      <iframe
        title="Gradio Chatbot"
        src="/gradio"
        className="w-full h-[calc(100vh-4rem)] border-none"
        allow="clipboard-read; clipboard-write;"
        scrolling="yes"
      />
    </div>
  );
}
