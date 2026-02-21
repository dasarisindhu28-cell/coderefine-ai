import gradio as gr
import os
from groq import Groq
from dotenv import load_dotenv

# =========================
# LOAD API KEY
# =========================
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# LANGUAGE EXTENSIONS
# =========================
EXTENSIONS = {
    "Python": ".py",
    "C": ".c",
    "C++": ".cpp",
    "Java": ".java",
    "JavaScript": ".js"
}
languages = list(EXTENSIONS.keys())

# =========================
# FUNCTIONS
# =========================
def ask_llm(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ Error:\n{e}"

def review_code(code, language):
    prompt = f"""
Analyze this {language} code.
Return:

Issues:
- ...

Fix Suggestions:
- ...

Formatted Code:
<corrected code>

Code:
{code}
"""
    result = ask_llm(prompt)
    if "Formatted Code:" in result:
        review_text, formatted = result.split("Formatted Code:", 1)
    else:
        review_text = result
        formatted = ""
    return review_text.strip(), formatted.strip()

def convert_code(code, source, target):
    prompt = f"""
Convert this {source} code to {target}.
Only output converted code.

Code:
{code}
"""
    return ask_llm(prompt)

def chat_fn(message, history):
    reply = ask_llm(message)
    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return "", history

def load_file(file):
    if file is None:
        return ""
    return open(file.name, "r", encoding="utf-8").read()

def save_file(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

def download_file(text, filename="formatted_code.py"):
    if not text:
        return None
    path = save_file(text, filename)
    return path

# =========================
# CSS STYLING
# =========================
custom_css = """
<style>
body {
    background: linear-gradient(135deg, #667eea, #764ba2);
    font-family: 'Inter', sans-serif;
    color: white;
}
h1, h2 {
    text-align:center;
    margin-bottom: 20px;
}
.menu-btn {
    display: block;
    width: 100%;
    background: linear-gradient(90deg, #ff7e5f, #feb47b);
    color: white;
    padding: 18px 20px;
    margin: 12px 0;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    text-align: left;
    cursor: pointer;
    transition: all 0.3s ease;
}
.menu-btn:hover {
    transform: scale(1.02);
    background: linear-gradient(90deg, #feb47b, #ff7e5f);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}
.menu-description {
    font-size: 14px;
    margin-left: 24px;
    color: rgba(255,255,255,0.9);
}
.back-btn {
    background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
    color: white !important;
    font-weight: bold !important;
}
.gradio-container > div {
    transition: opacity 0.4s ease;
}
.gradio-container > div[style*="display: none"] {
    opacity: 0;
    height: 0;
}
.gradio-container > div[style*="display: block"] {
    opacity: 1;
}
</style>
"""

# =========================
# GRADIO UI
# =========================
with gr.Blocks(title="CodeRefine AI") as demo:

    gr.HTML(custom_css)

    # ---------------------
    # HOME PAGE
    # ---------------------
    with gr.Column(visible=True) as home:
        gr.Markdown("# 🚀 CodeRefine AI")
        gr.Markdown("Your all-in-one coding assistant:\n\n- Analyze & fix your code\n- Convert between languages\n- Ask coding questions to AI")

        btn_review = gr.Button("🔍 Code Analysis", elem_classes="menu-btn")
        gr.Markdown("<div class='menu-description'>Analyze & fix your code</div>")

        btn_convert = gr.Button("🔄 Code Converter", elem_classes="menu-btn")
        gr.Markdown("<div class='menu-description'>Convert code between languages</div>")

        btn_chat = gr.Button("💬 AI Chatbot", elem_classes="menu-btn")
        gr.Markdown("<div class='menu-description'>Get coding help instantly</div>")

    # ---------------------
    # REVIEW PAGE
    # ---------------------
    with gr.Column(visible=False) as review_page:
        gr.Markdown("## 🔍 Code Analysis")
        back1 = gr.Button("⬅ Back", elem_classes="back-btn")

        file_upload = gr.File(label="Upload File")
        code_input = gr.Code(lines=15)
        file_upload.change(load_file, file_upload, code_input)

        lang = gr.Dropdown(languages, value="Python")
        run_btn = gr.Button("Analyze")

        review_output = gr.Textbox(label="Review", lines=8)
        formatted_output = gr.Code(label="Formatted Code")
        download_btn = gr.File(label="Download Formatted Code")

        def analyze(code, lang):
            review, formatted = review_code(code, lang)
            return review, formatted

        run_btn.click(analyze, [code_input, lang], [review_output, formatted_output])
        run_btn.click(lambda f: download_file(f), formatted_output, download_btn)

    # ---------------------
    # CONVERTER PAGE
    # ---------------------
    with gr.Column(visible=False) as convert_page:
        gr.Markdown("## 🔄 Code Converter")
        back2 = gr.Button("⬅ Back", elem_classes="back-btn")

        file2 = gr.File()
        code2 = gr.Code(lines=15)
        file2.change(load_file, file2, code2)

        src = gr.Dropdown(languages, value="Python")
        tgt = gr.Dropdown(languages, value="JavaScript")
        convert_btn = gr.Button("Convert")

        converted_output = gr.Code()
        download_convert = gr.File(label="Download Converted Code")

        convert_btn.click(convert_code, [code2, src, tgt], converted_output)
        convert_btn.click(lambda c: download_file(c), converted_output, download_convert)

    # ---------------------
    # CHAT PAGE
    # ---------------------
    with gr.Column(visible=False) as chat_page:
        gr.Markdown("## 💬 AI Chatbot")
        back3 = gr.Button("⬅ Back", elem_classes="back-btn")

        chatbot = gr.Chatbot(height=400)
        msg = gr.Textbox(placeholder="Ask coding questions...")
        msg.submit(chat_fn, [msg, chatbot], [msg, chatbot])

    # ---------------------
    # NAVIGATION FUNCTIONS
    # ---------------------
    def show_home():
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    def show_review():
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    def show_convert():
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
        )

    def show_chat():
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
        )

    # ---------------------
    # BUTTON CLICKS → NAVIGATION
    # ---------------------
    btn_review.click(show_review, outputs=[home, review_page, convert_page, chat_page])
    btn_convert.click(show_convert, outputs=[home, review_page, convert_page, chat_page])
    btn_chat.click(show_chat, outputs=[home, review_page, convert_page, chat_page])

    back1.click(show_home, outputs=[home, review_page, convert_page, chat_page])
    back2.click(show_home, outputs=[home, review_page, convert_page, chat_page])
    back3.click(show_home, outputs=[home, review_page, convert_page, chat_page])

# =========================
# LAUNCH
# =========================
port = int(os.environ.get("PORT", 10000))

demo.launch(
    server_name="0.0.0.0",
    server_port=port,
    share=False
)