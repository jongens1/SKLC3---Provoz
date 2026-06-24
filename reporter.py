import streamlit as st
from github import Github
import datetime

# --- KONFIGURÁCIA ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia ku GitHubu.")

st.set_page_config(page_title="Hlásenie Issue", layout="centered")

tab1, tab2 = st.tabs(["📢 Nahlásiť Issue", "🔍 Sledovať stav"])

# --- TAB 1: NAHLASOVANIE ---
with tab1:
    st.header("Nové Issue")
    with st.form("reporting_form", clear_on_submit=True):
        kategoria = st.selectbox("O aký problém ide?", 
            ["Autostore", "Práva/Access", "Odbáčanie na zjazdy/stanice", "Iné/Others"])
        nadpis = st.text_input("Stručný nadpis")
        detail = st.text_area("Detailný popis")
        uploaded_file = st.file_uploader("Pridať fotku / Odfotiť", type=["jpg", "jpeg", "png"])
        priorita = st.select_slider("Priorita", options=["Nízka", "Stredná", "Vysoká"])
        submit = st.form_submit_button("Odoslať nahlásenie")

    if submit and nadpis and detail:
        with st.spinner("Odosielam..."):
            image_url = ""
            if uploaded_file:
                path = f"attachments/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                repo.create_file(path, "Upload photo", uploaded_file.getvalue())
                image_url = f"https://raw.githubusercontent.com/{st.secrets['REPO_NAME']}/main/{path}"

            body = f"### Detail\n**Kategória:** {kategoria}\n**Priorita:** {priorita}\n\n**Popis:**\n{detail}"
            if image_url: body += f"\n\n**Príloha:**\n![Foto]({image_url})"
            
            repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body)
            st.success("✅ Nahlásené! Stav sledujte v druhej záložke.")

# --- TAB 2: SLEDOVANIE ---
with tab2:
    st.header("Stav nahlásených vecí")
    issues = repo.get_issues(state='all')[:15] # Posledných 15
    for issue in issues:
        icon = "🟠" if issue.state == "open" else "✅"
        with st.expander(f"{icon} #{issue.number}: {issue.title}"):
            st.markdown(issue.body)
            if issue.state == "closed":
                st.info(f"**Riešenie:** {issue.get_comments()[issue.get_comments().totalCount-1].body if issue.get_comments().totalCount > 0 else 'Vyriešené.'}")
