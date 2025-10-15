import uuid
import json
import streamlit as st
import streamlit.components.v1 as components
from config.config import get_config
from storage.json_store import JSONStore
from llm.engine import LLMEngine, GenerationParams, build_prompt


def _ensure_session_state(cfg):
    st.session_state.setdefault("project", None)
    st.session_state.setdefault("session_id", str(uuid.uuid4()))
    st.session_state.setdefault("history", [])  # current session items
    st.session_state.setdefault("liked", [])
    st.session_state.setdefault("tov_text", "")
    st.session_state.setdefault("last_generation", None)
    st.session_state.setdefault("output_area", "")


def copy_to_clipboard_button(text: str, key: str = "copy") -> None:
    safe = json.dumps(text)
    components.html(f"""
    <div>
      <button style="padding:6px 10px;" onclick='navigator.clipboard.writeText({safe});'>Copy to clipboard</button>
    </div>
    """, height=48)


def render(db: JSONStore):
    cfg = get_config()
    _ensure_session_state(cfg)

    st.subheader("Editor")

    if not st.session_state.get("project"):
        st.info("Select or create a project in the sidebar to start.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Initial text", key="input_text", height=200, placeholder="Paste or type initial copy…")
        st.text_area(
            "Optional instructions",
            key="custom_instructions",
            height=120,
            placeholder="e.g., emphasize benefits for SMBs, avoid jargon, include CTA",
        )
    with col2:
        strength = st.select_slider("Tone strength", options=["subtle", "balanced", "strong"], value="balanced")
        length = st.selectbox("Copy length", options=["short", "medium", "long"], index=1)
        tov_text = st.session_state.get("tov_text") or db.get_tone_of_voice()
        st.text_area("Tone of Voice (applied)", value=tov_text, key="tov_preview", height=220, disabled=True)

    engine = LLMEngine()
    def do_generate():
        tov = db.get_tone_of_voice()
        st.session_state["tov_text"] = tov
        params = GenerationParams(length=length, strength=strength)
        prompt = build_prompt(tov, st.session_state.get("input_text", ""), st.session_state.get("custom_instructions", ""), params)
        output = engine.generate(prompt, params)
        st.session_state["output_area"] = output
        item = {
            "input": st.session_state.get("input_text", ""),
            "instructions": st.session_state.get("custom_instructions", ""),
            "output": output,
            "liked": False,
            "params": {"length": length, "strength": strength},
        }
        st.session_state["history"].append(item)
        st.session_state["last_generation"] = item
        db.append_history_item(st.session_state["project"], st.session_state["session_id"], item)

    st.button("Generate", type="primary", on_click=do_generate, disabled=not (st.session_state.get("input_text") or st.session_state.get("custom_instructions")))

    last = st.session_state.get("last_generation")
    if last:
        st.markdown("---")
        st.markdown("**Output**")
        st.session_state["output_area"] = st.session_state.get("output_area", last["output"]) or last["output"]
        st.text_area("", key="output_area", height=240, disabled=True)
        bcol1, bcol2, bcol3 = st.columns(3)

        def do_regenerate():
            # regenerate with the same settings
            st.session_state["input_text"] = last["input"]
            st.session_state["custom_instructions"] = last["instructions"]
            params = GenerationParams(length=length, strength=strength)
            prompt = build_prompt(db.get_tone_of_voice(), last["input"], last["instructions"], params)
            out = engine.generate(prompt, params)
            st.session_state["output_area"] = out
            item = {**last, "output": out, "params": {"length": length, "strength": strength}}
            st.session_state["history"].append(item)
            st.session_state["last_generation"] = item
            db.append_history_item(st.session_state["project"], st.session_state["session_id"], item)

        def do_like():
            last["liked"] = True
            db.like_item(st.session_state["project"], last)
            st.success("Saved to Likes")

        with bcol1:
            st.button("Regenerate", on_click=do_regenerate)
        with bcol2:
            copy_to_clipboard_button(st.session_state.get("output_area", last["output"]), key="out_copy")
        with bcol3:
            st.button("Like", on_click=do_like)

    # Session history in this run
    if st.session_state.get("history"):
        with st.expander("Session History"):
            for idx, it in enumerate(reversed(st.session_state["history"])):
                st.markdown(f"### v{len(st.session_state['history']) - idx}")
                st.text(it["output"])
