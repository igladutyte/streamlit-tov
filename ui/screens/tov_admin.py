import streamlit as st
from storage.json_store import JSONStore


def render(db: JSONStore):
    st.subheader("Tone of Voice Admin")
    current = db.get_tone_of_voice()
    tov = st.text_area("Guidelines", value=current, height=300, placeholder="Paste tone of voice guidelines here…")
    if st.button("Save"):
        db.set_tone_of_voice(tov)
        st.session_state['tov_text'] = tov
        st.success("Tone of Voice updated")
