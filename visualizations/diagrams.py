def render_chatbot_pipeline_html() -> str:
    return """
<div class="glass">
  User or attacker input -> Defender -> Protected chatbot -> Evaluator -> Learner -> SQLite memory
</div>
"""


def render_memory_diagram_html() -> str:
    return """
<div class="glass">
  Structured memory stores interactions, learned patterns, defender rules, and RAG events.
</div>
"""


def render_architecture_diagram_html() -> str:
    return """
<div class="glass">
  Four agents cooperate in a closed feedback loop: Attacker, Defender, Evaluator, Learner.
</div>
"""
