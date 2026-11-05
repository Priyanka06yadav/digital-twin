
import uuid
import gradio as gr
import os
from agents import Runner, SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent

from main import agent


# VISITOR SESSION MANAGEMENT

def create_visitor_id():
    return f"visitor_{uuid.uuid4().hex}"


def get_session(visitor_id):
    return SQLiteSession(visitor_id, "conversations.db")

def reset_chat():
    return [], create_visitor_id(), "", gr.update(visible=True)


# CHAT RESPONSE WITH STREAMING

async def respond(message, history, visitor_id):

    if not message.strip():
        yield history, "", visitor_id
        return

    if not visitor_id:
        visitor_id = create_visitor_id()

    session = get_session(visitor_id)

    chat_history = list(history or [])

    chat_history.append({
        "role": "user",
        "content": message
    })

    chat_history.append({
        "role": "assistant",
        "content": ""
    })

    # Show the user's message immediately
    yield chat_history, "", visitor_id

    # Run the agent with SQLite conversation memory
    result = Runner.run_streamed(
        agent,
        message,
        session=session
    )

    # Display the answer as it is generated
    async for event in result.stream_events():

        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            chat_history[-1]["content"] += event.data.delta

            yield list(chat_history), "", visitor_id



# CUSTOM DARK THEME CSS


custom_css = """

/* Main background */
.gradio-container {
    background: #090909 !important;
    color: #f5f5f5 !important;
    max-width: 100% !important;
    padding: 0 !important;
}

/* Navigation bar */
#navbar {
    background: #090909;
    border-bottom: 1px solid #202020;
    padding: 12px 5%;
    min-height: 65px;
}

/* Center chatbot */
#chat-card {
    background: #151515;
    border: 1px solid #292929;
    border-radius: 30px;
    max-width: 1120px;
    min-width: 850px;
    margin: 30px auto;
    overflow: hidden;
}

/* Chat header */
#chat-header {
    background: #171717;
    padding: 20px 28px;
    border-bottom: 1px solid #292929;
}

/* Chatbot */
#chatbot {
    background: #121212 !important;
    border: none !important;
}

/* Welcome section */
#welcome {
    background: #121212;
    text-align: center;
    padding: 35px 20px 20px;
}

/* Bot icon */
#bot-avatar {
    width: 75px;
    height: 75px;
    border-radius: 50%;
    background: #222222;
    border: 1px solid #393939;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    font-size: 32px;
    color: #ff4b16;
}

/* Suggested question buttons */
.suggestion-btn {
    background: #1b1b1b !important;
    border: 1px solid #303030 !important;
    color: #dddddd !important;
    border-radius: 14px !important;
    text-align: left !important;
    min-height: 58px;
    transition: 0.2s ease;
}

.suggestion-btn:hover {
    background: #292929 !important;
    border-color: #ff4b16 !important;
}

/* Input area */
#input-area {
    background: #151515;
    border-top: 1px solid #292929;
    padding: 16px 22px;
}

/* Textbox */
#message-box textarea {
    background: #1c1c1c !important;
    color: white !important;
    border: 1px solid #363636 !important;
    border-radius: 18px !important;
    padding: 18px !important;
}

/* Send button */
#send-button {
    background: #ff4b16 !important;
    color: white !important;
    border-radius: 17px !important;
    min-width: 75px;
    min-height: 60px;
}

/* Reset button */
#reset-button {
    background: transparent !important;
    border: none !important;
    color: #999999 !important;
}

/* Scrollbar */
* {
    scrollbar-color: #555555 #151515;
}

/* Desktop-only layout */
body {
    min-width: 1100px;
}

"""



# BUILD THE GRADIO INTERFACE

dark_theme = gr.themes.Base(
    primary_hue="orange",
    secondary_hue="slate",
    neutral_hue="slate"
)

with gr.Blocks(
    title="Priyanka | AI Digital Twin"
) as demo:

    visitor_id = gr.State(create_visitor_id())

    # TOP NAVIGATION

    with gr.Row(elem_id="navbar", equal_height=True):

        gr.HTML("""
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="color:#ff4b16;font-size:27px;font-weight:bold;">
                    { }
                </span>
                <span style="font-size:22px;font-weight:800;
                             letter-spacing:3px;color:white;">
                    PRIYANKA.DEV
                </span>
            </div>
        """)

        gr.HTML("""
            <div style="display:flex;justify-content:flex-end;
                        gap:35px;padding-top:10px;">
                <a href="#about" style="color:#999;text-decoration:none;
                   font-weight:600;letter-spacing:1px;">ABOUT</a>
                <a href="#projects" style="color:#999;text-decoration:none;
                   font-weight:600;letter-spacing:1px;">PROJECTS</a>
                <a href="#chat" style="color:white;text-decoration:none;
                   font-weight:600;letter-spacing:1px;">CHAT</a>
            </div>
        """)

    # CENTER CHAT CARD

    with gr.Column(elem_id="chat-card"):

        # CHAT HEADER

        with gr.Row(elem_id="chat-header"):

            gr.HTML("""
                <div style="display:flex;align-items:center;gap:14px;">
                    <span style="height:11px;width:11px;
                        background:#10b981;border-radius:50%;
                        display:inline-block;"></span>
                    <span style="font-size:20px;font-weight:650;">
                        AI Digital Twin
                    </span>
                </div>
            """)

            reset_button = gr.Button(
                "↻",
                elem_id="reset-button",
                scale=0,
                min_width=55
            )

        # WELCOME SCREEN

        welcome = gr.Column(elem_id="welcome")

        with welcome:

            gr.HTML("""
                <div id="bot-avatar">♧</div>

                <h1 style="font-size:28px;font-weight:500;
                           margin-top:30px;color:#eeeeee;">
                    Hi, I'm Priyanka.
                </h1>

                <p style="font-size:21px;color:#b0b0b0;">
                    This AI is augmented by my work and experiences.
                </p>

                <p style="font-size:17px;color:#777;">
                    Ask me about my AI projects, professional
                    experience and technical skills.
                </p>
            """)

            gr.Markdown(" ")

            with gr.Column(scale=1):

                experience_btn = gr.Button(
                    "♙    Give me your 30-second introduction.",
                    elem_classes="suggestion-btn"
                )

                projects_btn = gr.Button(
                    "</>    Tell me about your recent projects.",
                    elem_classes="suggestion-btn"
                )

                skills_btn = gr.Button(
                    "✧    What are your technical skills?",
                    elem_classes="suggestion-btn"
                )

        # CONVERSATION WINDOW

        chatbot = gr.Chatbot(
            value=[],
            height=420,
            elem_id="chatbot"
        )

        # MESSAGE INPUT

        with gr.Row(elem_id="input-area"):

            message = gr.Textbox(
                placeholder="Ask my twin anything...",
                show_label=False,
                lines=1,
                max_lines=4,
                scale=8,
                elem_id="message-box"
            )

            send_button = gr.Button(
                "➤",
                elem_id="send-button",
                scale=1
            )

        gr.HTML("""
            <p style="text-align:center;color:#666;
                      font-size:11px;padding:0 10px 12px;">
                AI-generated responses · Powered by Gemini
            </p>
        """)

    # EVENT HANDLERS

    demo.load(
        fn=create_visitor_id,
        inputs=None,
        outputs=visitor_id
    )

    # Hide welcome screen when conversation starts

    def hide_welcome():
        return gr.update(visible=False)

    submit_event = message.submit(
        fn=hide_welcome,
        inputs=None,
        outputs=welcome
    ).then(
        fn=respond,
        inputs=[message, chatbot, visitor_id],
        outputs=[chatbot, message, visitor_id]
    )

    send_button.click(
        fn=hide_welcome,
        inputs=None,
        outputs=welcome
    ).then(
        fn=respond,
        inputs=[message, chatbot, visitor_id],
        outputs=[chatbot, message, visitor_id]
    )

    # SUGGESTED QUESTIONS

    experience_btn.click(
        fn=lambda: "Give me your 30-second introduction.",
        outputs=message
    )

    projects_btn.click(
        fn=lambda: "Tell me about your recent AI projects.",
        outputs=message
    )

    skills_btn.click(
        fn=lambda: "What are your technical skills?",
        outputs=message
    )

    # RESET CHAT

    reset_button.click(
        fn=reset_chat,
        inputs=None,
        outputs=[chatbot, visitor_id, message, welcome]
    )


# LAUNCH

demo.queue()

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        theme=dark_theme,
        css=custom_css
    )
