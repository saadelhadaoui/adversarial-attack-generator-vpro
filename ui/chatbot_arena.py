import json
import os
from html import escape
from datetime import datetime

import pandas as pd
import streamlit as st

from llm.client import LLMClient
from ui.components import pill
from ui.layout import render_section_header
from utils.attack_seed_loader import load_all_attack_seeds
from utils.chatbot_engine import (
    clear_learned_memory,
    empty_learned_memory,
    get_defender_rules,
    get_learned_patterns,
    get_metrics,
    get_rag_events,
    get_recent_interactions,
    process_chatbot_message,
)
from visualizations.diagrams import render_chatbot_pipeline_html


DEFAULT_DEMO_POLICY_PATH = "data/chatbot_demo_policy.json"


def _load_demo_policy() -> dict:
    path = os.getenv("CHATBOT_DEMO_POLICY_PATH", DEFAULT_DEMO_POLICY_PATH)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "default_mode": "PROTECTION",
        "controlled_mode": "CONTROLLED_EXFILTRATION",
        "button_modes": {},
        "prompts": {},
        "manual_tests": [],
        "live_scenarios": [],
        "trace_action_tones": {},
        "pill_action_tones": {},
    }


DEMO_POLICY = _load_demo_policy()


def _demo_prompt(key: str) -> str:
    return str(DEMO_POLICY.get("prompts", {}).get(key, ""))


def _demo_item_text(item: dict) -> str:
    prompt_key = item.get("prompt_key")
    if prompt_key:
        return _demo_prompt(str(prompt_key))
    return str(item.get("text", ""))


DEMO_TESTS = [(str(item.get("label", "Test")), _demo_item_text(item)) for item in DEMO_POLICY.get("manual_tests", [])]
LIVE_SCENARIOS = {
    str(item.get("family", "")): (str(item.get("label", "Scenario")), _demo_item_text(item))
    for item in DEMO_POLICY.get("live_scenarios", [])
}


def _init_state() -> None:
    defaults = {
        "defense_mode": DEMO_POLICY.get("default_mode", "PROTECTION"),
        "chatbot_messages": [],
        "chatbot_latest_trace": None,
        "chatbot_learned_memory": empty_learned_memory(),
        "live_traces": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _run(text: str, source: str = "user", mode: str | None = None) -> dict:
    active_mode = mode or st.session_state.defense_mode
    trace = process_chatbot_message(text, source=source, mode=active_mode)
    st.session_state.chatbot_latest_trace = trace
    st.session_state.chatbot_messages.append({"role": "user", "content": text})
    st.session_state.chatbot_messages.append({"role": "assistant", "content": trace["assistant_response"], "trace": trace})
    return trace


def _action_pill(action: str) -> str:
    return pill(action, DEMO_POLICY.get("pill_action_tones", {}).get(action, "muted"))


def _trace_value(value: object, max_len: int = 18) -> str:
    text = str(value)
    return text if len(text) <= max_len else f"{text[: max_len - 1]}..."


def _trace_item(label: str, value: object, tone: str = "muted", max_len: int = 18) -> str:
    return (
        '<div class="trace-item">'
        f'<div class="trace-label">{escape(label)}</div>'
        f'<div class="trace-value {escape(tone)}">{escape(_trace_value(value, max_len))}</div>'
        "</div>"
    )


def _render_trace(trace: dict | None) -> None:
    if not trace:
        st.info("No trace yet.")
        return
    d, e, lrn = trace["defender"], trace["evaluator"], trace["learner"]
    cb = trace.get("chatbot", {})
    action = d["action"]
    action_tone = DEMO_POLICY.get("trace_action_tones", {}).get(action, "muted")
    st.markdown(
        '<div class="trace-grid">'
        + _trace_item("Action", action, action_tone, 22)
        + _trace_item("Threat", d["threat_family"], "info", 20)
        + _trace_item("Risk", f"{d['risk_score']:.2f}", "warn")
        + _trace_item("Defense", f"{e['defense_score']:.2f}", "good")
        + _trace_item("Learned", "Yes" if lrn["memory_updated"] else "No", "good" if lrn["memory_updated"] else "muted")
        + _trace_item("LLM", "Used" if cb.get("llm_used") else "Fallback", "info" if cb.get("llm_used") else "muted")
        + "</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Full trace", expanded=False):
        st.json(trace)


def render_chatbot_arena() -> None:
    _init_state()
    render_section_header("04", "Interactive Arena", "Chatbot Arena", "Live defense pipeline with real Ollama, SQLite, and RAG.", "arena")
    st.markdown(render_chatbot_pipeline_html(), unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        modes = [DEMO_POLICY.get("default_mode", "PROTECTION"), DEMO_POLICY.get("controlled_mode", "CONTROLLED_EXFILTRATION")]
        st.radio("Defense mode", modes, key="defense_mode", horizontal=True)
    with c2:
        metrics = get_metrics()
        llm = LLMClient()
        health = llm.health()
        server_ok = health["server_available"]
        model_ok = health["model_available"]
        default_mode = DEMO_POLICY.get("default_mode", "PROTECTION")
        st.markdown(
            f"<b>Current Mode:</b> {pill(st.session_state.defense_mode, 'green' if st.session_state.defense_mode == default_mode else 'red')} "
            f"{pill(str(metrics.get('total_interactions', 0)) + ' interactions', 'purple')} "
            f"{pill(str(metrics.get('learned_patterns_count', 0)) + ' learned patterns', 'green')} "
            f"{pill(str(metrics.get('defender_rules_count', 0)) + ' rules', 'orange')} "
            f"{pill('ollama online' if server_ok else 'ollama offline', 'green' if server_ok else 'red')} "
            f"{pill('14b model ready' if model_ok else '14b model missing', 'green' if model_ok else 'orange')}",
            unsafe_allow_html=True,
        )
        if not server_ok:
            st.caption(f"Ollama is not reachable at `{health['host']}`. Start it with `ollama serve` or set `OLLAMA_HOST`.")
        elif not model_ok:
            available = ", ".join(health["available_models"][:4]) or "none"
            st.caption(
                f"Ollama is online at `{health['host']}`, but `{health['model']}` is not available. "
                f"Run `ollama pull {health['model']}`. Visible models: {available}"
            )

    tab_chat, tab_tests, tab_live = st.tabs(["Chat", "Manual Tests", "Live Defense Run"])

    with tab_chat:
        left, right = st.columns([1.35, 1])
        with left:
            for msg in st.session_state.chatbot_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    trace = msg.get("trace")
                    if trace:
                        st.markdown(_action_pill(trace["defender"]["action"]), unsafe_allow_html=True)
            with st.form("arena_chat_form", clear_on_submit=True):
                text_col, send_col = st.columns([5, 1])
                user_text = text_col.text_input(
                    "Message",
                    placeholder="Ask a question or paste a [redacted ...] test pattern",
                    label_visibility="collapsed",
                )
                submitted = send_col.form_submit_button("Send", use_container_width=True)
        with right:
            st.markdown('<div class="glass"><span class="eyebrow">Latest Verdict</span>', unsafe_allow_html=True)
            _render_trace(st.session_state.chatbot_latest_trace)
            st.markdown("</div>", unsafe_allow_html=True)
        if submitted and user_text:
            _run(user_text)
            st.rerun()

    with tab_tests:
        st.caption("These are safe synthetic prompts. In CONTROLLED_EXFILTRATION mode, first-time attack variants can penetrate for learning; repeats should block.")
        cols = st.columns(3)
        for index, (label, text) in enumerate(DEMO_TESTS):
            col = cols[index % len(cols)]
            if col.button(label, use_container_width=True):
                _run(text, source="manual_test")
                st.rerun()
            col.caption(text)

    with tab_live:
        st.write("Use this sequence to show adaptation: first controlled attempt penetrates safely, learns, then the repeat is blocked.")
        scenarios = LIVE_SCENARIOS
        traces = st.session_state.live_traces
        b1, b2, b3, b4 = st.columns(4)
        if b1.button("Reset learned memory", use_container_width=True):
            clear_learned_memory()
            st.session_state.live_traces = {}
            st.rerun()
        if b2.button("Protection block", use_container_width=True):
            traces["protection_block"] = _run(
                _demo_prompt("data_exfiltration"),
                "manual_test",
                mode=DEMO_POLICY.get("button_modes", {}).get("protection_block", DEMO_POLICY.get("default_mode", "PROTECTION")),
            )
            st.rerun()
        if b3.button("Benign pass", use_container_width=True):
            traces["benign"] = _run(
                _demo_prompt("benign"),
                "manual_test",
                mode=DEMO_POLICY.get("button_modes", {}).get("benign_pass", DEMO_POLICY.get("default_mode", "PROTECTION")),
            )
            st.rerun()
        if b4.button("Run all controlled", use_container_width=True):
            for family, (_, text) in scenarios.items():
                controlled_mode = DEMO_POLICY.get("button_modes", {}).get(
                    "controlled",
                    DEMO_POLICY.get("controlled_mode", "CONTROLLED_EXFILTRATION"),
                )
                traces[f"{family}_first"] = _run(text, "manual_test", mode=controlled_mode)
                traces[f"{family}_repeat"] = _run(text, "manual_test", mode=controlled_mode)
            st.rerun()

        for family, (label, text) in scenarios.items():
            st.markdown(f"#### {label}")
            c1, c2, c3 = st.columns([1, 1, 2])
            if c1.button(f"First {label}", key=f"{family}_first_btn", use_container_width=True):
                traces[f"{family}_first"] = _run(
                    text,
                    "manual_test",
                    mode=DEMO_POLICY.get("button_modes", {}).get("controlled", DEMO_POLICY.get("controlled_mode", "CONTROLLED_EXFILTRATION")),
                )
                st.rerun()
            if c2.button(f"Repeat {label}", key=f"{family}_repeat_btn", use_container_width=True):
                traces[f"{family}_repeat"] = _run(
                    text,
                    "manual_test",
                    mode=DEMO_POLICY.get("button_modes", {}).get("controlled", DEMO_POLICY.get("controlled_mode", "CONTROLLED_EXFILTRATION")),
                )
                st.rerun()
            c3.code(text, language="text")
            left, right = st.columns(2)
            with left:
                st.caption("First controlled attempt")
                _render_trace(traces.get(f"{family}_first"))
            with right:
                st.caption("Repeat attempt")
                _render_trace(traces.get(f"{family}_repeat"))

def render_chatbot_results_section() -> None:
    _init_state()
    render_section_header(
        "05",
        "Results",
        "Arena results dashboard",
        "Latest trace, SQLite rows, learned memory, and loaded attack seeds.",
        "results",
    )
    tab_trace, tab_db, tab_seeds = st.tabs(["Latest Trace", "Database", "Seeds"])

    with tab_trace:
        _render_trace(st.session_state.chatbot_latest_trace)
        if st.session_state.chatbot_latest_trace:
            st.download_button(
                "Export trace JSON",
                data=json.dumps(st.session_state.chatbot_latest_trace, indent=2, default=str),
                file_name=f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )

    with tab_db:
        st.subheader("Learned patterns")
        st.dataframe(pd.DataFrame(get_learned_patterns()), use_container_width=True)
        st.subheader("Defender rules")
        st.dataframe(pd.DataFrame(get_defender_rules()), use_container_width=True)
        st.subheader("Recent interactions")
        st.dataframe(pd.DataFrame(get_recent_interactions(25)), use_container_width=True)
        st.subheader("RAG events")
        st.dataframe(pd.DataFrame(get_rag_events(25)), use_container_width=True)

    with tab_seeds:
        st.dataframe(pd.DataFrame(load_all_attack_seeds()), use_container_width=True)
