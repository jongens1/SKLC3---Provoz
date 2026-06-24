import streamlit as st
from github import Github
import time

try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia.")

st.set_page_config(page_title="Solver Admin", layout="wide")

col_t, col_r = st.columns([4, 1])
with col_t: st.title("🛠 Solver Dashboard")
with col_r: 
    if st.button("🔄 Aktualizovať"): st.rerun()

password = st.text_input("Admin heslo", type="password")
if password == st.secrets["ADMIN_PASSWORD"]:
    issues = repo.get_issues(state='open')
    st.write(f"Otvorené incidenty: **{issues.totalCount}**")
    
    for issue in issues:
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### #{issue.number}: {issue.title}")
                st.markdown(issue.body)
            with c2:
                note = st.text_input("Poznámka pre užívateľa", key=f"n_{issue.number}")
                
                # TLAČIDLO 1: Len pridá komentár
                if st.button("💬 POSLAŤ POZNÁMKU", key=f"msg_{issue.number}", use_container_width=True):
                    if note:
                        issue.create_comment(f"**Update:** {note}")
                        st.toast("Poznámka odoslaná!")
                        time.sleep(1)
                        st.rerun()
                
                # TLAČIDLO 2: Vyrieši a zatvorí
                if st.button("✅ VYRIEŠIŤ A ZATVORIŤ", key=f"close_{issue.number}", use_container_width=True):
                    issue.create_comment(f"**Riešenie:** {note if note else 'Vyriešené.'}")
                    issue.edit(state='closed')
                    st.success("Uzatvorené!")
                    time.sleep(1.5)
                    st.rerun()
        st.divider()
