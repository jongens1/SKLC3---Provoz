import streamlit as st
from github import Github
import time

# --- KONFIGURÁCIA ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia ku GitHubu.")

st.set_page_config(page_title="Solver Admin", layout="wide")

# --- HLAVIČKA A REFRESH ---
col_t, col_r = st.columns([4, 1])
with col_t: 
    st.title("🛠 Solver Dashboard")
with col_r: 
    if st.button("🔄 Refresh"): 
        st.rerun()

# --- LOGIN SYSTÉM ---
password = st.text_input("Zadaj svoje osobné heslo", type="password")

# Overenie, či heslo existuje v našej tabuľke SOLVERS
if password in st.secrets["SOLVERS"]:
    solver_name = st.secrets["SOLVERS"][password] # Získame meno podľa hesla
    
    st.sidebar.success(f"Prihlásený: **{solver_name}**")
    
    issues = repo.get_issues(state='open')
    st.write(f"Počet otvorených incidentov: **{issues.totalCount}**")
    st.divider()

    if issues.totalCount == 0:
        st.success("Všetko je vyriešené!")
    
    for issue in issues:
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### #{issue.number}: {issue.title}")
                st.markdown(issue.body)
                st.caption(f"Nahlásené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
            
            with c2:
                note = st.text_input("Poznámka pre užívateľa", key=f"n_{issue.number}")
                
                # POSLAŤ POZNÁMKU
                if st.button("💬 POSLAŤ POZNÁMKU", key=f"msg_{issue.number}", use_container_width=True):
                    if note:
                        # V komentári sa zobrazí aj meno riešiteľa
                        full_note = f"**Status (riešiteľ {solver_name}):** {note}"
                        issue.create_comment(full_note)
                        st.toast("Poznámka odoslaná!")
                        time.sleep(1)
                        st.rerun()
                
                # VYRIEŠIŤ
                if st.button("✅ VYRIEŠIŤ", key=f"close_{issue.number}", use_container_width=True):
                    full_resolve = f"✅ **Vyriešil {solver_name}**\n**Poznámka:** {note if note else 'Bez ďalšieho komentára.'}"
                    issue.create_comment(full_resolve)
                    issue.edit(state='closed')
                    st.success("Uzatvorené!")
                    time.sleep(1.5)
                    st.rerun()
            st.divider()
else:
    if password != "":
        st.error("Nesprávne osobné heslo!")
