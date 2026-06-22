import streamlit as st
from github import Github

# --- 1. KONFIGURÁCIA A PRIPOJENIE ---
# Tieto údaje čerpá zo "Secrets" v Streamlit Cloude
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception as e:
    st.error("Chyba pripojenia ku GitHubu. Skontrolujte nastavenie Secrets.")

st.set_page_config(page_title="Hlásenie prevádzkových problémov", layout="centered")

# --- 2. HLAVNÉ MENU (ZÁLOŽKY) ---
tab_report, tab_solver = st.tabs(["📢 Nahlásiť problém", "🛠 Solver (Admin)"])

# --- 3. ZÁLOŽKA: NAHLASOVANIE ---
with tab_report:
    st.header("Nový prevádzkový problém")

    with st.form("reporting_form", clear_on_submit=True):
        st.info("Vyberte kategóriu a popíšte problém. Po odoslaní ho začneme riešiť.")
        
        kategoria = st.selectbox(
            "O aký problém ide?",
            [
                "Autostore", 
                "Práva/Access", 
                "Odbáčanie na zjazdy/stanice/Turning to shipping lanes/stations", 
                "Vytvorenie lokácií/New locations", 
                "Chyby aktivácie/Activation error", 
                "Neprepisovanie stavov/Job states stucked", 
                "Iné/Others"
            ]
        )
        
        nadpis = st.text_input("Stručný nadpis (napr. Zablokovaná brána)")
        detail = st.text_area("Detailný popis problému")
        priorita = st.select_slider("Priorita", options=["Nízka", "Stredná", "Vysoká"])

        submit = st.form_submit_button("Odoslať nahlásenie")

    if submit:
        if not nadpis or not detail:
            st.warning("Prosím, vyplňte nadpis aj detailný popis.")
        else:
            try:
                # Formátovanie textu, ktorý sa uloží do GitHubu
                body_text = f"**Kategória:** {kategoria}\n"
                body_text += f"**Priorita:** {priorita}\n"
                body_text += f"**Nahlásil:** Používateľ cez aplikáciu\n"
                body_text += f"--- \n\n**Detailný popis:**\n{detail}"
                
                # Vytvorenie Issue (bez labels, aby to nepadalo)
                repo.create_issue(
                    title=f"[{kategoria}] {nadpis}",
                    body=body_text
                )
                
                st.success("✅ Problém bol úspešne nahlásený. Ďakujeme!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Chyba pri odosielaní na GitHub: {e}")

# --- 4. ZÁLOŽKA: SOLVER (ADMIN) ---
with tab_solver:
    st.header("Administrácia pre riešiteľa")

    password = st.text_input("Zadaj prístupové heslo", type="password")

    if password == st.secrets["ADMIN_PASSWORD"]:
        st.subheader("Aktuálne otvorené incidenty")

        # Načítanie otvorených issues z GitHubu
        issues = repo.get_issues(state='open')

        if issues.totalCount == 0:
            st.info("Všetko je vyriešené. Žiadne otvorené problémy!")
        else:
            for issue in issues:
                # Každý problém zabalíme do rozbaľovacieho okna
                with st.expander(f"#{issue.number}: {issue.title}"):
                    st.markdown(issue.body)
                    st.caption(f"Vytvorené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
                    
                    # Tlačidlo na vyriešenie (uzavretie issue)
                    if st.button(f"Označiť ako VYRIEŠENÉ", key=f"btn_{issue.number}"):
                        issue.create_comment("✅ Vyriešené cez aplikáciu.")
                        issue.edit(state='closed')
                        st.success(f"Problém #{issue.number} bol uzavretý.")
                        st.rerun()
                st.divider()
    elif password != "":
        st.error("Nesprávne heslo!")
