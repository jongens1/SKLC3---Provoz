import streamlit as st
from github import Github
import time

# --- KONFIGURÁCIA ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia.")

st.set_page_config(page_title="Solver Admin", layout="wide")

st.title("🛠 Solver Dashboard")

# Odporúčam nechať heslo ako poistku, aj keď link nikto nemá
password = st.text_input("Admin heslo", type="password")
if password == st.secrets["ADMIN_PASSWORD"]:
    issues = repo.get_issues(state='open')
    
    if issues.totalCount == 0:
        st.success("Všetko je čisté! Žiadne otvorené issues.")
    
    for issue in issues:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### #{issue.number}: {issue.title}")
            st.markdown(issue.body)
        with col2:
            st.write("---")
            note = st.text_input("Poznámka pre užívateľa", key=f"n_{issue.number}")
            if st.button("VYRIEŠENÉ", key=f"b_{issue.number}", use_container_width=True):
                issue.create_comment(note if note else "Vyriešené.")
                issue.edit(state='closed')
                st.toast("Uzavreté!")
                time.sleep(1)
                st.rerun()
        st.divider()
