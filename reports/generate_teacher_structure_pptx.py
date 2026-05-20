from __future__ import annotations

from pathlib import Path

import generate_editable_project_pptx as deck


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "Adaptive_Multi_Agent_LLM_Defense_Lab_TEACHER_STRUCTURE_EDITABLE.pptx"


def build_teacher_slides() -> list[deck.Slide]:
    slides: list[deck.Slide] = []

    s = deck.Slide("Title")
    s.add_bg()
    s.image(deck.screenshot("logo-vert.png"), 0.65, 0.52, 4.8, 1.7, "EMSI Logo")
    s.image(deck.screenshot("WhatsApp Image 2026-05-15 at 13.20.45.jpeg"), 9.72, 0.52, 2.28, 1.72, "EMSI Student Lab Logo")
    s.text(0.75, 2.78, 8.3, 0.62, "Adaptive Multi-Agent", 40, deck.WHITE, True)
    s.text(0.75, 3.42, 8.3, 0.7, "LLM Defense Lab", 42, deck.CYAN, True)
    s.rect(0.75, 4.20, 6.1, 0.04, deck.CYAN, deck.CYAN)
    s.text(0.75, 4.58, 8.7, 0.62, "Adaptive AI Security Through Agentic Defense, Live Memory, and Controlled Demonstration", 21, deck.WHITE, True)
    s.text(0.75, 5.55, 4.9, 0.44, "Author: Saad El Hadaoui", 18, deck.WHITE, True, fill=deck.NAVY2, line=deck.CYAN, radius=True)
    s.text(0.75, 6.08, 6.1, 0.44, "Institution: EMSI - Ecole Marocaine des Sciences de l'Ingenieur", 15, deck.MUTED, fill=deck.NAVY2, line=deck.CYAN, radius=True)
    s.text(7.15, 5.55, 4.65, 0.97, "Final Technical Presentation\nStreamlit | Ollama | SQLite | Multi-Agent Defense", 16, deck.WHITE, True, fill=deck.CARD, line=deck.CYAN, radius=True)
    slides.append(s)

    s = deck.Slide("Summary Context")
    s.add_bg()
    s.title_block("01", "Summary, Motivation, Context", "Why this project matters and where it fits in AI security.")
    s.card(0.75, 2.05, 3.65, 1.05, "Summary", "A live defense lab that protects an LLM chatbot using defender, evaluator, learner, and memory components.", deck.CYAN)
    s.card(0.75, 3.35, 3.65, 1.05, "Motivation", "LLM applications can be manipulated by prompt injection, jailbreak attempts, and data exfiltration prompts.", deck.ORANGE)
    s.card(0.75, 4.65, 3.65, 1.05, "Context", "Chatbots are increasingly connected to tools, databases, documents, and internal workflows.", deck.GREEN)
    s.image(deck.screenshot("Screenshot 2026-05-15 130530.png"), 4.95, 1.98, 7.55, 4.88, "Application Overview Screenshot")
    slides.append(s)

    s = deck.Slide("State Gap")
    s.add_bg()
    s.title_block("02", "State of the Art and Research Gap", "Existing defenses help, but many remain static or disconnected from memory.")
    s.text(0.75, 2.0, 5.5, 3.65, "State of the Art\n\n• System prompts and policy instructions\n• Keyword filters and rule-based guardrails\n• Moderation classifiers\n• RAG filtering and document access rules\n• Red-team datasets and human evaluation\n• Prompt injection and jailbreak benchmark suites", 18, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    s.text(6.75, 2.0, 5.5, 3.65, "Research Gap\n\n• Static filters do not adapt to new attack variants\n• Many defenses do not store reusable memory\n• Evaluation is often separate from the running app\n• Demonstrations rarely show learning after failure\n• Need a safe way to show attacks without real data leakage", 18, deck.WHITE, fill=deck.CARD, line=deck.ORANGE, radius=True)
    s.text(1.1, 6.1, 10.8, 0.54, "Project idea: connect defense, evaluation, learning, and persistent memory in one visible live loop.", 19, deck.GREEN, True, fill=deck.NAVY2, line=deck.GREEN, radius=True)
    slides.append(s)

    s = deck.Slide("Framework")
    s.add_bg()
    s.title_block("03", "Proposed Framework", "Full system pipeline and toolchain used in the project.")
    boxes = [
        ("User Prompt", 0.65, 2.45, deck.BLUE),
        ("Defender Agent", 2.55, 2.45, deck.CYAN),
        ("Protected Chatbot", 4.75, 2.45, deck.GREEN),
        ("Evaluator Agent", 7.05, 2.45, deck.ORANGE),
        ("Learning Agent", 9.25, 2.45, deck.PURPLE),
        ("SQLite Memory", 5.85, 4.15, deck.CYAN),
    ]
    for label, x, y, color in boxes:
        s.text(x, y, 1.65, 0.62, label, 13, deck.WHITE, True, fill=deck.CARD, line=color, radius=True, margin=50000)
    s.arrow(2.3, 2.76, 2.54, 2.76)
    s.arrow(4.2, 2.76, 4.74, 2.76)
    s.arrow(6.4, 2.76, 7.04, 2.76)
    s.arrow(8.7, 2.76, 9.24, 2.76)
    s.arrow(10.05, 3.08, 6.72, 4.15)
    s.arrow(6.72, 4.15, 3.38, 3.08)
    s.text(0.75, 5.25, 5.4, 1.22, "Tools\nPython, Streamlit, Ollama, qwen2.5:14b-instruct-q4_K_M, SQLite, Plotly, local RAG-style retrieval, custom DefenseGraph orchestration.", 16, deck.WHITE, fill=deck.NAVY2, line=deck.CYAN, radius=True)
    s.image(deck.screenshot("Screenshot 2026-05-15 131115.png"), 6.55, 4.85, 5.8, 1.62, "Architecture Screenshot")
    slides.append(s)

    s = deck.Slide("Agents")
    s.add_bg()
    s.title_block("04", "Agent-by-Agent Explanation", "Each component has one clear role in the defense loop.")
    s.card(0.65, 1.95, 2.85, 1.1, "Defender Agent", "Classifies risk and decides PASS, BLOCK, REFORMULATE, or ALLOW_WITH_MONITORING.", deck.CYAN)
    s.card(3.85, 1.95, 2.85, 1.1, "Protected Chatbot", "Answers safe prompts with Ollama and refuses blocked requests.", deck.GREEN)
    s.card(7.05, 1.95, 2.85, 1.1, "Evaluator Agent", "Checks synthetic leaks, false positives, and defense score.", deck.ORANGE)
    s.card(10.25, 1.95, 2.35, 1.1, "Learning Agent", "Stores attack patterns and new rules in SQLite.", deck.PURPLE)
    s.image(deck.screenshot("Screenshot 2026-05-15 131001.png"), 0.85, 3.45, 11.65, 3.0, "Agents Screenshot")
    slides.append(s)

    s = deck.Slide("LLM Evaluation")
    s.add_bg()
    s.title_block("05", "LLM Evaluation and Local Configuration", "The model runs locally, while the defense pipeline controls and evaluates interactions.")
    s.text(0.75, 2.0, 5.4, 2.15, "Local Configuration\n\n• Runtime: local machine\n• LLM backend: Ollama\n• Model: qwen2.5:14b-instruct-q4_K_M\n• Frontend: Streamlit\n• Database: data/defense_lab.db\n• Evaluation history: SQLite tables", 17, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    s.text(0.75, 4.55, 5.4, 1.75, "Evaluation Metrics\n\n• Defense score\n• Attack success rate\n• Defense success rate\n• False positive rate\n• Learned pattern count", 17, deck.WHITE, fill=deck.CARD, line=deck.GREEN, radius=True)
    s.image(deck.screenshot("Screenshot 2026-05-15 131250.png"), 6.55, 1.9, 5.75, 4.75, "Evaluation Metrics Screenshot")
    slides.append(s)

    s = deck.Slide("Training Results")
    s.add_bg()
    s.title_block("06", "Results of Training and Adaptation", "The system learns from a controlled synthetic breach and blocks repeated variants.")
    s.text(0.75, 1.95, 4.95, 3.35, "Observed Result\n\n1. Start with fresh memory\n2. Run a controlled attack demo\n3. System allows monitored synthetic output\n4. Evaluator detects attack success\n5. Learner stores the pattern\n6. Repeat attack is blocked\n7. Charts and tables update from SQLite", 17, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    s.image(deck.screenshot("Screenshot 2026-05-15 130638.png"), 6.05, 1.88, 3.08, 2.32, "First Attempt")
    s.image(deck.screenshot("Screenshot 2026-05-15 131044.png"), 9.25, 1.88, 3.08, 2.32, "Evidence")
    s.image(deck.screenshot("Screenshot 2026-05-15 131059.png"), 6.05, 4.42, 6.28, 2.0, "Memory Results")
    slides.append(s)

    s = deck.Slide("Limitations Future Work")
    s.add_bg()
    s.title_block("07", "Limitations and Future Work", "What the current prototype does well, and what should come next.")
    s.text(0.75, 2.0, 5.45, 3.85, "Limitations\n\n• Demonstration uses synthetic data only\n• Defense rules are simplified for a lab prototype\n• Prompt classification can still miss new variants\n• Performance depends on local hardware and model speed\n• More benchmark testing is needed\n• Current UI is focused on demonstration rather than deployment", 17, deck.WHITE, fill=deck.CARD, line=deck.ORANGE, radius=True)
    s.text(6.75, 2.0, 5.45, 3.85, "Future Work\n\n• Add larger benchmark datasets\n• Improve semantic memory retrieval\n• Compare several local and cloud LLMs\n• Add user roles and access control\n• Add automated test suites for attacks\n• Deploy as a full web service\n• Build stronger reporting and export tools", 17, deck.WHITE, fill=deck.CARD, line=deck.GREEN, radius=True)
    slides.append(s)

    s = deck.Slide("Conclusion")
    s.add_bg()
    s.title_block("08", "Conclusion", "The project demonstrates adaptive, observable, memory-driven LLM defense.")
    s.text(0.9, 2.1, 5.65, 3.55, "Conclusion\n\nThe system shows that LLM security can move beyond static blocking.\n\nBy combining a Defender Agent, Protected Chatbot, Evaluator Agent, Learning Agent, and SQLite memory, the application can detect risky prompts, evaluate outcomes, learn patterns, and improve future decisions.", 19, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    s.text(7.05, 2.1, 4.75, 2.15, "Final Message\n\nAdaptive defense is essential for safer AI applications.", 25, deck.GREEN, True, fill=deck.NAVY2, line=deck.GREEN, radius=True)
    s.text(7.05, 4.65, 4.75, 1.0, "Ready for live demonstration with Streamlit, Ollama, SQLite, and real project screenshots.", 18, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    slides.append(s)

    s = deck.Slide("References")
    s.add_bg()
    s.title_block("09", "References", "Main documentation, security guidance, and project resources.")
    s.text(0.8, 2.0, 5.65, 3.9, "Technical References\n\n• Ollama documentation\n• Streamlit documentation\n• SQLite documentation\n• Plotly documentation\n• Python documentation\n• Project source code and screenshots", 18, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    s.text(6.9, 2.0, 5.35, 3.9, "Security References\n\n• OWASP Top 10 for LLM Applications\n• Prompt injection research papers\n• Jailbreak and adversarial prompt datasets\n• Hugging Face adversarial prompt collections\n• Safe red-team evaluation practices", 18, deck.WHITE, fill=deck.CARD, line=deck.CYAN, radius=True)
    s.text(0.8, 6.25, 11.45, 0.45, "Adaptive Multi-Agent LLM Defense Lab - EMSI Final Project Presentation", 18, deck.CYAN, True)
    slides.append(s)

    return slides


def main():
    deck.PPTX_PATH = OUT
    slides = build_teacher_slides()
    deck.make_pptx(slides)
    print(OUT)


if __name__ == "__main__":
    main()
