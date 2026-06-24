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

# --- HLAVIČKA A REFRESH ---
col_t, col_r = st.columns([4, 1])
with col_t:
    st.title("🛠 Solver Dashboard")
with col_r:
    if st.button("🔄 Aktualizovať"):
        st.rerun()

# --- HESLO ---
password = st.text_input("Admin heslo", type="password")
if password == st.secrets["ADMIN_PASSWORD"]:
    
    # Načítanie otvorených issues
    issues = repo.get_issues(state='open')
    
    st.write(f"Počet otvorených incidentov: **{issues.totalCount}**")
    st.divider()

    if issues.totalCount == 0:
        st.success("Všetko je čisté! Žiadne otvorené issues.")
    
    for issue in issues:
        # Vytvoríme biely box pre každý incident
        with st.container():
            c1, c2 = st.columns([3, 1])
            
            with c1:
                st.markdown(f"### #{issue.number}: {issue.title}")
                st.markdown(issue.body)
                st.caption(f"Nahlásené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
            
            with c2:
                # Políčko na poznámku
                note = st.text_input("Poznámka k riešeniu", 
                                    placeholder="Napr. Opravené / Hotovo",
                                    key=f"note_{issue.number}")
                
                # Tlačidlo na potvrdenie
                if st.button("✅ VYRIEŠIŤ", key=f"btn_{issue.number}", use_container_width=True):
                    if not note:
                        st.error("Napíš aspoň krátku poznámku!")
                    else:
                        with st.spinner("Uzatváram..."):
                            issue.create_comment(f"**Riešenie:** {note}")
                            issue.edit(state='closed')
                            st.success("Uzavreté!")
                            time.sleep(1.5) # Dôležitá pauza pre GitHub API
                            st.rerun()
            st.divider()
else:
    if password != "":
        st.error("Nesprávne heslo!")
