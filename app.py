import gradio as gr
from query import ask

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="The Unofficial Guide — Sac State CS") as demo:
    gr.Markdown("# The Unofficial Guide: Sac State CS Professors")
    gr.Markdown("Ask anything about CS professors at Sacramento State — teaching style, exams, office hours, and more. Answers are grounded in real student reviews.")

    inp = gr.Textbox(label="Your question", placeholder="e.g. Which professor has the most useful lectures?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
