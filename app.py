import streamlit as st
from pathlib import Path
from config.config import get_config
from storage.json_store import JSONStore
from ui.screens import editor as editor_screen
from ui.screens import history as history_screen
from ui.screens import tov_admin as tov_admin_screen

cfg = get_config()
db = JSONStore(cfg.db_file)

# App title and layout
st.set_page_config(page_title=cfg.app_name, layout="wide")
st.title(cfg.app_name)

# Sidebar: project management and navigation
def ensure_session_defaults():
    st.session_state.setdefault('project', db.get_active_project())
    st.session_state.setdefault('page', 'Editor')
    if st.session_state['project'] is None:
        # bootstrap with a default project if none exist
        projects = db.list_projects()
        if not projects:
            db.create_project('Default Project')
            st.session_state['project'] = 'Default Project'
        else:
            st.session_state['project'] = projects[0]
            db.set_active_project(projects[0])

ensure_session_defaults()

if st.session_state.get('navigate_to_editor'):
    st.session_state['page'] = 'Editor'
    del st.session_state['navigate_to_editor']

with st.sidebar:
    st.header('Projects')
    existing = db.list_projects()
    current = st.selectbox('Active project', options=existing, index=(existing.index(st.session_state['project']) if st.session_state['project'] in existing and existing else 0) if existing else None, key='project_select')
    if current and current != st.session_state['project']:
        st.session_state['project'] = current
        db.set_active_project(current)

    new_name = st.text_input('New project name', value='', placeholder='Enter name…')
    cols = st.columns([1,1])
    with cols[0]:
        if st.button('Create') and new_name.strip():
            db.create_project(new_name.strip())
            st.session_state['project'] = new_name.strip()
    with cols[1]:
        if st.button('Delete') and st.session_state['project']:
            db.delete_project(st.session_state['project'])
            st.session_state['project'] = db.get_active_project()

    st.markdown('---')
    st.header('Navigation')
    st.radio('Go to', options=['Editor', 'History', 'Tone of Voice Admin'], label_visibility='collapsed', key='page')

# Route to screens
page = st.session_state.get('page', 'Editor')
if page == 'Editor':
    editor_screen.render(db)
elif page == 'History':
    history_screen.render(db)
else:
    tov_admin_screen.render(db)
