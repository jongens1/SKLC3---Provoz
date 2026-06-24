import streamlit as st
from github import Github
import datetime

try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia.")

st.set_page_config(page_title="Hlásenie Issue", layout="centered")
tab1, tab2 = st.tabs(["📢 Nahlásiť Issue", "🔍 Sledovať stav"])

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
        # ... (kód na odosielanie zostáva rovnaký ako predtým) ...
        image_url = ""
        if uploaded_file:
            path = f"attachments/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            repo.create_file(path, "Upload photo", uploaded_file.getvalue())
            image_url = f"https://raw.githubusercontent.com/{st.secrets['REPO_NAME']}/main/{path}"
        body = f"### Detail\n**Kategória:** {kategoria}\n**Priorita:** {priorita}\n\n**Popis:**\n{detail}"
        if image_url: body += f"\n\n**Príloha:**\n![Foto]({image_url})"
        repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body)
        st.success("✅ Nahlásené!")

with tab2:
    st.header("Stav nahlásených vecí")
    issues = repo.get_issues(state='all')[:15]
    for issue in issues:
        icon = "🟠" if issue.state == "open" else "✅"
        with st.expander(f"{icon} #{issue.number}: {issue.title}"):
            st.markdown(issue.body)
            st.divider()
            # ZOBRAZENIE KOMENTÁROV (všetkých)
            comments = issue.get_comments()
            if comments.totalCount > 0:
                st.write("**Aktualizácie od riešiteľa:**")
                for comment in comments:
                    st.info(comment.body)
            elif issue.state == "closed":
                st.success("Vyriešené.")
