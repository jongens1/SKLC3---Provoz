import streamlit as st
from github import Github
import datetime

# --- 1. KONFIGURÁCIA ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia ku GitHubu.")

st.set_page_config(page_title="Hlásenie Issue", layout="centered")

# --- HLAVIČKA S REFRESH TLAČIDLOM ---
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("Issue Systém")
with col_refresh:
    if st.button("🔄 Refresh"):
        st.rerun()

tab1, tab2 = st.tabs(["📢 Nahlásiť Issue", "🔍 Sledovať stav"])

# --- 2. ZÁLOŽKA: NAHLASOVANIE ---
with tab1:
    st.header("Nové Issue")
    with st.form("reporting_form", clear_on_submit=True):
        kategoria = st.selectbox("Kategória", ["Autostore", "Práva/Access", "Odbáčanie na zjazdy/stanice", "Iné/Others"])
        nadpis = st.text_input("Stručný nadpis")
        detail = st.text_area("Detailný popis")
        uploaded_file = st.file_uploader("Pridať fotku / Odfotiť", type=["jpg", "jpeg", "png"])
        priorita = st.select_slider("Priorita", options=["Nízka", "Stredná", "Vysoká"])
        submit = st.form_submit_button("Odoslať nahlásenie")

    if submit and nadpis and detail:
        with st.spinner("Odosielam..."):
            try:
                image_url = ""
                if uploaded_file:
                    path = f"attachments/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    repo.create_file(path, "Upload photo", uploaded_file.getvalue())
                    image_url = f"https://raw.githubusercontent.com/{st.secrets['REPO_NAME']}/main/{path}"

                body = f"### Detail\n**Kategória:** {kategoria}\n**Priorita:** {priorita}\n\n**Popis:**\n{detail}"
                if image_url: body += f"\n\n**Príloha:**\n![Foto]({image_url})"
                
                repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body)
                st.success("✅ Nahlásené! Pre overenie stavu kliknite na 'Sledovať stav'.")
                st.balloons()
            except Exception as e:
                st.error(f"Chyba: {e}")

# --- 3. ZÁLOŽKA: SLEDOVANIE ---
with tab2:
    st.header("Stav nahlásených vecí")
    st.write("Kliknite na 🔄 **Refresh** vpravo hore pre aktualizáciu stavu.")
    
    # Načítanie posledných 15 issues (otvorené aj zatvorené)
    issues = repo.get_issues(state='all', sort='created', direction='desc')[:15]
    
    if not issues:
        st.info("Zatiaľ neboli nahlásené žiadne issues.")
    
    for issue in issues:
        icon = "🟠" if issue.state == "open" else "✅"
        with st.expander(f"{icon} #{issue.number}: {issue.title}"):
            st.markdown(issue.body)
            st.caption(f"Vytvorené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
            
            st.divider()
            
            # ZOBRAZENIE KOMENTÁROV (Statusov od riešiteľa)
            comments = issue.get_comments()
            if comments.totalCount > 0:
                st.write("**Aktualizácie od riešiteľa:**")
                for comment in comments:
                    # Každý komentár dáme do modrého boxu
                    st.info(comment.body)
            else:
                if issue.state == "open":
                    st.write("🕒 Čaká sa na vyjadrenie riešiteľa.")
                else:
                    st.success("Tento problém bol vyriešený.")
