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

st.set_page_config(page_title="Issue Reporting", layout="centered")

# --- 2. MENU ---
tab_report, tab_solver = st.tabs(["📢 Nahlásiť Issue", "🛠 Solver (Admin)"])

# --- 3. ZÁLOŽKA: NAHLASOVANIE ---
with tab_report:
    st.header("Nové Issue")

    with st.form("reporting_form", clear_on_submit=True):
        kategoria = st.selectbox(
            "O aký problém ide?",
            ["Autostore", "Práva/Access", "Odbáčanie na zjazdy/stanice", 
             "Vytvorenie lokácií/New locations", "Chyby aktivácie/Activation error", 
             "Neprepisovanie stavov/Job states stucked", "Iné/Others"]
        )
        
        nadpis = st.text_input("Stručný nadpis")
        detail = st.text_area("Detailný popis")
        
        # PRIDANIE FOTKY
        uploaded_file = st.file_uploader("Pridať fotku / Odfotiť", type=["jpg", "jpeg", "png"])
        
        priorita = st.select_slider("Priorita", options=["Nízka", "Stredná", "Vysoká"])
        submit = st.form_submit_button("Odoslať nahlásenie")

    if submit:
        if not nadpis or not detail:
            st.warning("Prosím, vyplňte nadpis aj detail.")
        else:
            with st.spinner("Odosielam hlásenie..."):
                try:
                    image_url = ""
                    # Ak používateľ nahral fotku, uložíme ju do GitHubu do priečinka 'attachments'
                    if uploaded_file is not None:
                        file_path = f"attachments/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                        file_content = uploaded_file.getvalue()
                        repo.create_file(file_path, f"Upload image for {nadpis}", file_content)
                        # Vytvorenie priameho linku na zobrazenie fotky
                        image_url = f"https://raw.githubusercontent.com/{st.secrets['REPO_NAME']}/main/{file_path}"

                    # Formátovanie textu (používame bežný text, nie nadpisy, aby to nebolo obrie)
                    body_text = f"### Detail hlásenia\n"
                    body_text += f"**Kategória:** {kategoria}  \n" # Dve medzery na konci robia nový riadok
                    body_text += f"**Priorita:** {priorita}  \n\n"
                    body_text += f"**Popis:**  \n{detail}  \n\n"
                    
                    if image_url:
                        body_text += f"**Príloha:**  \n![Fotka]({image_url})"

                    # Vytvorenie Issue
                    repo.create_issue(
                        title=f"[{kategoria}] {nadpis}",
                        body=body_text
                    )
                    
                    st.success("✅ Issue bolo úspešne nahlásené!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Chyba: {e}")

# --- 4. ZÁLOŽKA: SOLVER (ADMIN) ---
with tab_solver:
    st.header("Administrácia")
    password = st.text_input("Zadaj prístupové heslo", type="password")

    if password == st.secrets["ADMIN_PASSWORD"]:
        st.subheader("Aktuálne otvorené issues")
        
        # Načítame issues a vypneme cache, aby sme mali vždy čerstvé dáta
        issues = repo.get_issues(state='open')

        if issues.totalCount == 0:
            st.info("Žiadne otvorené problémy.")
        else:
            for issue in issues:
                with st.container():
                    # Zobrazenie v expanderi pre čistý dizajn
                    with st.expander(f"#{issue.number}: {issue.title}"):
                        st.markdown(issue.body)
                        st.caption(f"Vytvorené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
                        
                        # Tlačidlo na vyriešenie
                        if st.button(f"✅ Označiť ako VYRIEŠENÉ", key=f"btn_{issue.number}"):
                            with st.spinner("Aktualizujem stav na GitHube..."):
                                issue.create_comment("Problém vyriešený cez aplikáciu.")
                                issue.edit(state='closed')
                                st.toast(f"Issue #{issue.number} uzavreté!")
                                # DÔLEŽITÉ: Malá pauza, aby GitHub stihol spracovať zmenu
                                time.sleep(1) 
                                st.rerun()
                    st.divider()
    elif password != "":
        st.error("Nesprávne heslo!")
