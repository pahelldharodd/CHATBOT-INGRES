import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import your chatbot modules
from ai import GroundwaterRAGChatbot, RAGResponse
from vector_store import GroundwaterEmbeddingPipeline

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🌊 Groundwater Analysis Chatbot",
    page_icon="🌊",
    layout="centered"
)

# Custom CSS for clean styling
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #ddd;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #1976d2;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #7b1fa2;
    }
    
    .system-status {
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .status-ready { background-color: #e8f5e8; color: #2e7d32; }
    .status-error { background-color: #ffebee; color: #c62828; }
    .status-warning { background-color: #fff3e0; color: #ef6c00; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None

if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False

def check_api_key():
    """Check if API key is available"""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return True, "✅ API Key loaded successfully"
    else:
        return False, "❌ GEMINI_API_KEY not found in environment variables"

def initialize_chatbot():
    """Initialize the chatbot system"""
    try:
        # Initialize embedding pipeline
        embedding_pipeline = GroundwaterEmbeddingPipeline()
        
        # Try to load existing embeddings
        embeddings_path = "./embeddings_data"
        chunks_file = "groundwater_chunks.json"
        
        if os.path.exists(embeddings_path):
            st.info("📂 Loading existing embeddings...")
            embedding_pipeline.load_embeddings(embeddings_path)
            st.success("✅ Embeddings loaded successfully")
        elif os.path.exists(chunks_file):
            st.info("🔄 Creating new embeddings from chunks file...")
            embedding_pipeline.create_embeddings_from_json(chunks_file)
            embedding_pipeline.build_faiss_index(index_type='flat')
            embedding_pipeline.save_embeddings(embeddings_path)
            st.success("✅ New embeddings created and saved")
        else:
            st.error(f"❌ Neither embeddings ({embeddings_path}) nor chunks file ({chunks_file}) found")
            return None
        
        # Initialize chatbot
        chatbot = GroundwaterRAGChatbot(embedding_pipeline)
        return chatbot
        
    except Exception as e:
        st.error(f"❌ Error initializing chatbot: {str(e)}")
        return None

def display_chat_message(role, content, metadata=None):
    """Display a chat message with proper styling"""
    if role == "user":
        with st.container():
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>{content}
            </div>
            """, unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong><br>{content}
            </div>
            """, unsafe_allow_html=True)
            
            # Show metadata if available
            if metadata:
                cols = st.columns(3)
                with cols[0]:
                    st.caption(f"Confidence: {metadata.get('confidence', 0):.1%}")
                with cols[1]:
                    st.caption(f"Chunks: {metadata.get('chunks', 0)}")
                with cols[2]:
                    st.caption(f"Type: {metadata.get('type', 'N/A')}")

def main():
    # Header
    st.title("🌊 Groundwater Data Analysis Chatbot")
    st.markdown("Ask questions about groundwater assessment data for India (2023-2024)")
    
    # System status check
    api_available, api_message = check_api_key()
    
    if api_available:
        st.markdown(f'<div class="system-status status-ready">{api_message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="system-status status-error">{api_message}</div>', unsafe_allow_html=True)
        st.info("💡 Please create a `.env` file with your `GEMINI_API_KEY=your_api_key_here`")
        st.stop()
    
    # Initialize chatbot if not already done
    if not st.session_state.system_initialized and api_available:
        with st.spinner("🚀 Initializing chatbot system..."):
            chatbot = initialize_chatbot()
            if chatbot:
                st.session_state.chatbot = chatbot
                st.session_state.system_initialized = True
                st.rerun()
    
    # Show system status
    if st.session_state.system_initialized:
        st.markdown('<div class="system-status status-ready">🤖 Chatbot ready to answer your questions!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="system-status status-warning">⚠️ System not initialized</div>', unsafe_allow_html=True)
        if st.button("🔄 Retry Initialization"):
            st.rerun()
        return
    
    # Sidebar with sample questions
    with st.sidebar:
        st.header("💡 Sample Questions")
        sample_questions = [
            "How many districts in Maharashtra improved from 2023 to 2024?",
            "What percentage of Rajasthan's units are over-exploited in 2024?",
            "Show deteriorated assessment units across all states",
            "Which states had districts move from Critical to Semi-Critical?",
            "Compare Safe vs Over-exploited units nationally"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(f"Q{i+1}: {question[:30]}...", key=f"sample_{i}"):
                # Add question to messages and process it
                st.session_state.messages.append({"role": "user", "content": question})
                # Process the question
                with st.spinner("🔍 Analyzing..."):
                    try:
                        response = st.session_state.chatbot.chat(question)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response.answer,
                            "metadata": {
                                "confidence": response.confidence,
                                "chunks": response.retrieved_chunks,
                                "type": response.query_type.replace('_', ' ').title()
                            }
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        # Export chat button
        if st.session_state.messages and st.button("📥 Export Chat"):
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages
            }
            st.download_button(
                "Download Chat History",
                data=json.dumps(chat_data, indent=2),
                file_name=f"groundwater_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Display chat history
    if st.session_state.messages:
        st.markdown("---")
        for message in st.session_state.messages:
            display_chat_message(
                message["role"], 
                message["content"], 
                message.get("metadata")
            )
    else:
        # Welcome message
        st.markdown("""
        ### 👋 Welcome!
        
        I can help you analyze groundwater assessment data for India. Here are some things you can ask:
        
        - 📊 **Statistics by state**: "How many units improved in Maharashtra?"
        - 🔢 **Percentages**: "What percentage of units are over-exploited in Rajasthan?"
        - 📈 **Comparisons**: "Compare 2023 vs 2024 data for Punjab"
        - 🎯 **Trends**: "Which states had the most improvements?"
        
        **Start by typing your question below or use the sample questions in the sidebar!**
        """)
    
    # Chat input
    st.markdown("---")
    user_input = st.text_input(
        "Your question:",
        placeholder="e.g., How many districts in Gujarat are over-exploited in 2024?",
        key="user_input"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("Send 📤", type="primary")
    
    # Process user input
    if (send_button or user_input) and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner("🔍 Analyzing your question..."):
            try:
                response = st.session_state.chatbot.chat(user_input)
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response.answer,
                    "metadata": {
                        "confidence": response.confidence,
                        "chunks": response.retrieved_chunks,
                        "type": response.query_type.replace('_', ' ').title()
                    }
                })
                
                # Clear input and refresh
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing your question: {str(e)}")
                st.info("Please try rephrasing your question or check if the system is properly initialized.")

if __name__ == "__main__":
    main()