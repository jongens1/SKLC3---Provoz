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
        st.subheader("Kontaktné údaje")
        c1, c2 = st.columns(2)
        with c1:
            meno = st.text_input("Meno / Login *")
            oddelenie = st.text_input("Oddelenie *")
        with c2:
            kontakt = st.text_input("T.č. / Kontakt *")
        
        st.divider()
        st.subheader("Detail problému")
        
        kategoria = st.selectbox("O aký problém ide?", ["Autostore", "Práva/Access", "Odbáčanie na zjazdy/stanice", "Iné/Others"])
        nadpis = st.text_input("Stručný nadpis *")
        detail = st.text_area("Detailný popis *")
        
        uploaded_file = st.file_uploader("Pridať fotku / Odfotiť", type=["jpg", "jpeg", "png"])
        priorita = st.select_slider("Priorita", options=["Nízka", "Stredná", "Vysoká"])
        
        st.caption("* Povinné polia")
        submit = st.form_submit_button("Odoslať nahlásenie")

    # Validácia: Musia byť vyplnené kontaktné údaje aj popis
    if submit:
        if not (meno and oddelenie and kontakt and nadpis and detail):
            st.error("Prosím, vyplňte všetky povinné polia označené hviezdičkou (*).")
        else:
            with st.spinner("Odosielam..."):
                try:
                    image_url = ""
                    if uploaded_file:
                        path = f"attachments/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                        repo.create_file(path, "Upload photo", uploaded_file.getvalue())
                        image_url = f"https://raw.githubusercontent.com/{st.secrets['REPO_NAME']}/main/{path}"

                    # Formátovanie správy pre GitHub
                    body = f"### 👤 Kontakt na nahlasovateľa\n"
                    body += f"- **Meno:** {meno}\n"
                    body += f"- **Oddelenie:** {oddelenie}\n"
                    body += f"- **Kontakt:** {kontakt}\n\n"
                    body += f"### 📝 Detail hlásenia\n"
                    body += f"**Kategória:** {kategoria} | **Priorita:** {priorita}\n\n"
                    body += f"**Popis:**\n{detail}"
                    
                    if image_url:
                        body += f"\n\n**Príloha:**\n![Foto]({image_url})"
                    
                    repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body)
                    st.success("✅ Nahlásené! Ďakujeme za informácie.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Chyba: {e}")

# --- 3. ZÁLOŽKA: SLEDOVANIE ---
with tab2:
    st.header("Stav nahlásených vecí")
    issues = repo.get_issues(state='all', sort='created', direction='desc')[:15]
    
    for issue in issues:
        icon = "🟠" if issue.state == "open" else "✅"
        with st.expander(f"{icon} #{issue.number}: {issue.title}"):
            st.markdown(issue.body)
            st.divider()
            comments = issue.get_comments()
            if comments.totalCount > 0:
                st.write("**Aktualizácie od riešiteľa:**")
                for comment in comments:
                    st.info(comment.body)
            else:
                if issue.state == "open":
                    st.write("🕒 Čaká sa na vyjadrenie riešiteľa.")
                else:
                    st.success("Tento problém bol vyriešený.")
