import streamlit as st
from storage.json_store import JSONStore


def render(db: JSONStore):
    st.subheader("History")
    project = st.session_state.get("project")
    if not project:
        st.info("Select a project in the sidebar.")
        return
    sessions = db.list_sessions(project)
    likes = db.list_likes(project)

    st.markdown("### Sessions")
    if not sessions:
        st.write("No sessions yet.")
    for session in reversed(sessions):
        with st.expander(f"Session {session['id']}"):
            for idx, item in enumerate(session.get('items', []), start=1):
                st.markdown(f"**v{idx}** — {item['params']['length']}, {item['params']['strength']}")
                st.text_area("Output", value=item['output'], key=f"s_{session['id']}_{idx}", height=160)
                cols = st.columns(2)
                with cols[0]:
                    if st.button("Restore to editor", key=f"restore_{session['id']}_{idx}"):
                        st.session_state['last_generation'] = item
                        st.session_state['input_text'] = item['input']
                        st.session_state['custom_instructions'] = item['instructions']
                        st.session_state['output_area'] = item['output']
                        st.session_state['navigate_to_editor'] = True
                        st.rerun()
                with cols[1]:
                    if st.button("Like", key=f"like_{session['id']}_{idx}"):
                        db.like_item(project, item)
                        st.success("Saved to Likes")

    st.markdown("### Likes")
    if not likes:
        st.write("No liked items yet.")
    for i, item in enumerate(reversed(likes), start=1):
        st.text_area("Output", value=item['output'], key=f"l_{i}", height=140)
