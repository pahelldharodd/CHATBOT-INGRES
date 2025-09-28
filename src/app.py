import gradio as gr
from utils.upload_file import UploadFile
from utils.chatbot import ChatBot
from utils.ui_settings import UISettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Custom CSS for futuristic glassmorphism theme
custom_css = """
/* Futuristic Glassmorphism Theme */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-bg: #030714;
    --glass-bg: rgba(15, 23, 42, 0.3);
    --glass-border: rgba(6, 182, 212, 0.2);
    --glass-hover: rgba(6, 182, 212, 0.1);
    --cyan-primary: #06b6d4;
    --cyan-secondary: #0891b2;
    --teal-primary: #14b8a6;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --text-accent: #67e8f9;
}

/* Main container styling */
.gradio-container, body, #root {
    background: linear-gradient(135deg, #030714 0%, #0f172a 50%, #1e293b 100%) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    min-height: 100vh !important;
    height: auto !important;
    overflow-y: auto !important;
    color: var(--text-primary) !important;
}

/* Larger chatbot container with scrolling */
.chatbot {
    height: 60vh !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
}

/* Flexible app interface */
.gradio-container .app {
    min-height: 100vh !important;
    height: auto !important;
    padding: 2rem 1rem 1rem 1rem !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Minimize header padding */
.gradio-container .app > .container {
    padding: 0 !important;
}

/* Compact input area */
.gradio-container .wrap {
    margin: 0.25rem 0 !important;
}

/* Remove extra margins from components */
.gradio-container .form {
    gap: 0.25rem !important;
}

/* Animated background effects */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 0% 0%, rgba(26, 54, 93, 0.4) 0%, transparent 50%),
        radial-gradient(circle at 100% 100%, rgba(13, 148, 136, 0.4) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(30, 64, 175, 0.4) 0%, transparent 50%);
    animation: gradientPulse 6s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes gradientPulse {
    0%, 100% { opacity: 0.4; }
    33% { opacity: 0.6; }
    66% { opacity: 0.5; }
}

/* Ensure content is above background */
.gradio-container > *, .main > * {
    position: relative !important;
    z-index: 1 !important;
}

/* Enhanced glassmorphism blocks */
.block, .form, .panel {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(6, 182, 212, 0.2) !important;
    border-radius: 1.5rem !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

/* Chatbot styling */
.chat-container {
    background: rgba(15, 23, 42, 0.3) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    border-radius: 1.5rem !important;
    box-shadow: 0 8px 32px rgba(6, 182, 212, 0.1) !important;
}

/* Chat messages */
.message {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(6, 182, 212, 0.2) !important;
    border-radius: 1rem !important;
    margin: 0.5rem 0 !important;
    color: var(--text-primary) !important;
}

/* Input styling */
.futuristic-input textarea, input[type="text"] {
    background: rgba(15, 23, 42, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    border-radius: 1rem !important;
    color: var(--text-primary) !important;
    padding: 1rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.futuristic-input textarea:focus, input[type="text"]:focus {
    border-color: var(--cyan-primary) !important;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.4) !important;
    outline: none !important;
}

.futuristic-input textarea::placeholder, input[type="text"]::placeholder {
    color: var(--text-secondary) !important;
}

/* Button styling */
.primary-btn, button.primary {
    background: linear-gradient(135deg, var(--cyan-primary), var(--teal-primary)) !important;
    border: none !important;
    border-radius: 0.75rem !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.primary-btn:hover, button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4) !important;
}

.upload-btn {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.8), rgba(79, 70, 229, 0.8)) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    border-radius: 0.75rem !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

.clear-btn, button.secondary {
    background: linear-gradient(135deg, rgba(71, 85, 105, 0.8), rgba(51, 65, 85, 0.8)) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(71, 85, 105, 0.3) !important;
    border-radius: 0.75rem !important;
    color: var(--text-primary) !important;
    transition: all 0.3s ease !important;
}

/* Dropdown styling */
.settings-dropdown select, select {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    border-radius: 0.75rem !important;
    color: var(--text-primary) !important;
    padding: 0.75rem !important;
}

.settings-dropdown select:hover, select:hover {
    border-color: var(--cyan-primary) !important;
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.3) !important;
}

/* Tab styling */
.tab-nav button {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(6, 182, 212, 0.2) !important;
    border-radius: 0.75rem !important;
    color: var(--text-primary) !important;
    transition: all 0.3s ease !important;
    margin: 0 0.25rem !important;
}

.tab-nav button:hover {
    background: rgba(6, 182, 212, 0.1) !important;
    border-color: var(--cyan-primary) !important;
    color: var(--text-accent) !important;
}

.tab-nav button.selected {
    background: rgba(6, 182, 212, 0.2) !important;
    border-color: var(--cyan-primary) !important;
    color: var(--text-accent) !important;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.3) !important;
}

/* Accordion styling */
.accordion-header {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(6, 182, 212, 0.2) !important;
    border-radius: 0.75rem !important;
    color: var(--text-primary) !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(to bottom, var(--cyan-primary), var(--teal-primary));
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(to bottom, var(--cyan-secondary), var(--teal-primary));
}

/* Like/dislike buttons */
.feedback-buttons {
    filter: brightness(0) saturate(100%) invert(71%) sepia(39%) saturate(5839%) hue-rotate(159deg) brightness(94%) contrast(87%);
}

.feedback-buttons:hover {
    filter: brightness(0) saturate(100%) invert(91%) sepia(97%) saturate(4796%) hue-rotate(159deg) brightness(106%) contrast(89%);
}
"""

with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="cyan",
        secondary_hue="blue", 
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
    ).set(
        # Button styling
        button_primary_background_fill="#06b6d4",
        button_primary_background_fill_hover="#0891b2", 
        button_primary_border_color="transparent",
        button_primary_text_color="white",
        
        # Input styling
        input_background_fill="rgba(15, 23, 42, 0.5)",
        input_border_color="rgba(6, 182, 212, 0.3)",
        
        # Block styling  
        block_background_fill="rgba(15, 23, 42, 0.3)",
        block_border_color="rgba(6, 182, 212, 0.2)"
    ),
    css=custom_css,
    title="🌊 INGRES AI Assistant",
    head="""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """
) as demo:
    # Header section with branding
    with gr.Row():
        gr.HTML("""
        <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(20, 184, 166, 0.1)); border-radius: 1.5rem; margin-bottom: 2rem; border: 1px solid rgba(6, 182, 212, 0.2);">
            <h1 style="font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #06b6d4, #14b8a6); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">
                🌊 INGRES AI Assistant
            </h1>
            <p style="font-size: 1.2rem; color: #94a3b8; margin: 0.5rem 0 0 0;">
                Intelligent Groundwater Analysis with Dual AI Capabilities
            </p>
        </div>
        """)
    
    with gr.Tabs():
        with gr.TabItem("🤖 AI Chat Assistant"):
            # Assistant type selector - COMMENTED OUT FOR COMPACT UI
            # with gr.Row():
            #     gr.HTML("""
            #     <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 1rem; padding: 1.5rem; margin-bottom: 1rem;">
            #         <h3 style="color: #67e8f9; margin: 0 0 1rem 0; font-size: 1.3rem;">Choose Your AI Assistant Mode:</h3>
            #         <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            #             <div style="background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 0.75rem; padding: 1rem;">
            #                 <div style="color: #06b6d4; font-weight: 600; margin-bottom: 0.5rem;">📊 Database Query Mode</div>
            #                 <div style="color: #cbd5e1; font-size: 0.9rem;">Query INGRES groundwater database with natural language</div>
            #             </div>
            #             <div style="background: rgba(20, 184, 166, 0.1); border: 1px solid rgba(20, 184, 166, 0.3); border-radius: 0.75rem; padding: 1rem;">
            #                 <div style="color: #14b8a6; font-weight: 600; margin-bottom: 0.5rem;">📚 Knowledge Assistant Mode</div>
            #                 <div style="color: #cbd5e1; font-size: 0.9rem;">Explore CGWB reports and understand technical terms</div>
            #             </div>
            #         </div>
            #     </div>
            #     """)
            
            ##############
            # Chat Interface
            ##############
            with gr.Row() as row_one:
                chatbot = gr.Chatbot(
                    value=[],
                    type="messages",
                    elem_id="futuristic-chatbot",
                    height=400,
                    show_label=False,
                    container=True,
                    elem_classes=["chat-container"],
                    avatar_images=(
                        "https://img.icons8.com/fluency/48/user-male-circle.png", 
                        "https://img.icons8.com/fluency/48/chatbot.png"
                    )
                )
                # **Adding like/dislike icons
                chatbot.like(UISettings.feedback, None, None)
            
            ##############
            # Input Section
            ##############
            with gr.Row():
                input_txt = gr.Textbox(
                    lines=3,
                    scale=8,
                    placeholder="💬 Ask about groundwater data, technical terms, or upload files for analysis...",
                    container=False,
                    elem_classes=["futuristic-input"],
                    label="",
                    show_label=False
                )
            
            ##############
            # Control Panel
            ##############
            with gr.Row() as control_panel:
                with gr.Column(scale=2):
                    text_submit_btn = gr.Button(
                        value="🚀 Send Message", 
                        elem_classes=["primary-btn"],
                        variant="primary"
                    )
                with gr.Column(scale=2):
                    upload_btn = gr.UploadButton(
                        "📁 Upload Data Files", 
                        file_types=['.csv', '.xlsx'], 
                        file_count="multiple",
                        elem_classes=["upload-btn"]
                    )
                with gr.Column(scale=2):
                    clear_button = gr.Button(
                        "🗑️ Clear Chat",
                        elem_classes=["clear-btn"],
                        variant="secondary"
                    )
            
            ##############
            # Settings Panel - HIDDEN FOR COMPACT UI
            ##############
            # with gr.Row():
            #     with gr.Accordion("⚙️ Advanced Settings", open=False):
            #         with gr.Row():
            app_functionality = gr.Dropdown(
                label="🔧 App Functionality", 
                choices=["Chat", "Process files"], 
                value="Chat",
                visible=False
            )
            chat_type = gr.Dropdown(
                label="🤖 Chat Assistant Type", 
                choices=[
                    "📊 Database Query Assistant - INGRES SQL Data",
                    "📚 Knowledge Assistant - CGWB Reports & Terms",
                    # "🔍 Hybrid Mode - SQL + RAG Combined"
                ], 
                value="📊 Database Query Assistant - INGRES SQL Data",
                visible=False
            )
            ##############
            # Process:
            ##############
            file_msg = upload_btn.upload(fn=UploadFile.run_pipeline, inputs=[
                upload_btn, chatbot, app_functionality], outputs=[input_txt, chatbot], queue=False)

            txt_msg = input_txt.submit(fn=ChatBot.respond,
                                       inputs=[chatbot, input_txt,
                                               chat_type, app_functionality],
                                       outputs=[input_txt,
                                                chatbot],
                                       queue=False).then(lambda: gr.Textbox(interactive=True),
                                                         None, [input_txt], queue=False)

            txt_msg = text_submit_btn.click(fn=ChatBot.respond,
                                            inputs=[chatbot, input_txt,
                                                    chat_type, app_functionality],
                                            outputs=[input_txt,
                                                     chatbot],
                                            queue=False).then(lambda: gr.Textbox(interactive=True),
                                                              None, [input_txt], queue=False)

app = FastAPI(title="INGRES AI Assistant API")

# Static files removed - using embedded CSS instead

# Allow local dev frontend to access the backend-mounted Gradio app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:7860",
        "http://127.0.0.1:7860",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Gradio UI at /gradio
gr.mount_gradio_app(app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
