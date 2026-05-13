import streamlit as st


def render_final_section() -> None:
    st.markdown(
        '<div class="glass"><h2>Ready for safe demonstration</h2><p>Run the arena tests to populate memory, metrics, and charts.</p></div>',
        unsafe_allow_html=True,
    )
