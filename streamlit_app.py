import streamlit as st
from github import Github
import datetime
import time

# --- 1. KONFIGURÁCIA ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception as e:
    st.error("Chyba pripojenia ku GitHubu.")

st.set_page_config(page_title="Issue Tracking System", layout="centered")

# --- 2. MENU (PRIDANÁ ZÁLOŽKA SLEDOVAŤ) ---
tab_report, tab_track, tab_solver = st.tabs(["📢 Nahlásiť Issue", "🔍 Sledovať stav", "🛠 Solver (Admin)"])

# --- 3. ZÁLOŽKA: NAHLASOVANIE ---
with tab_report:
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
            image_url = ""
            if uploaded_file:
                file_path = f"attachments/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                repo.create_file(file_path, f"Upload image", uploaded_file.getvalue())
                image_url = f"https://raw.githubusercontent.com/{st.secrets['REPO_NAME']}/main/{file_path}"

            body_text = f"### Detail hlásenia\n**Kategória:** {kategoria}  \n**Priorita:** {priorita}  \n\n**Popis:**  \n{detail}"
            if image_url: body_text += f"\n\n**Príloha:**  \n![Fotka]({image_url})"

            repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body_text)
            st.success("✅ Nahlásené! Stav môžete sledovať v záložke 'Sledovať stav'.")
            st.balloons()

# --- 4. ZÁLOŽKA: SLEDOVANIE (NOVÁ) ---
with tab_track:
    st.header("Prehľad nahlásených problémov")
    st.info("Tu môžete vidieť stav posledných 15 nahlásených incidentov.")

    # Načítame posledných 15 issues (všetky stavy: otvorené aj zatvorené)
    all_issues = repo.get_issues(state='all', sort='created', direction='desc')[:15]

    for issue in all_issues:
        status_icon = "🟠 V riešení" if issue.state == "open" else "✅ Vyriešené"
        
        with st.expander(f"{status_icon} | #{issue.number}: {issue.title}"):
            st.markdown(issue.body)
            st.caption(f"Vytvorené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
            
            # Ak je issue vyriešené, zobrazíme posledný komentár (tvoje vysvetlenie)
            if issue.state == "closed":
                comments = issue.get_comments()
                if comments.totalCount > 0:
                    st.info(f"**Vyjadrone riešiteľa:** {comments[comments.totalCount - 1].body}")
                st.success("Tento problém bol úspešne uzavretý.")

# --- 5. ZÁLOŽKA: SOLVER (ADMIN) ---
with tab_solver:
    st.header("Administrácia")
    password = st.text_input("Zadaj prístupové heslo", type="password")

    if password == st.secrets["ADMIN_PASSWORD"]:
        st.subheader("Otvorené issues")
        open_issues = repo.get_issues(state='open')

        if open_issues.totalCount == 0:
            st.info("Žiadne otvorené problémy.")
        else:
            for issue in open_issues:
                with st.expander(f"#{issue.number}: {issue.title}"):
                    st.markdown(issue.body)
                    
                    # Solver môže pridať krátky komentár k riešeniu
                    solver_comment = st.text_input("Poznámka k riešeniu (uvidí ju nahlasovateľ)", key=f"comm_{issue.number}")
                    
                    if st.button(f"✅ Vyriešené", key=f"btn_{issue.number}"):
                        with st.spinner("Uzatváram..."):
                            # Ak solver napísal komentár, uložíme ho
                            comment_text = solver_comment if solver_comment else "Problém bol vyriešený."
                            issue.create_comment(comment_text)
                            issue.edit(state='closed')
                            time.sleep(1)
                            st.rerun()
                st.divider()
