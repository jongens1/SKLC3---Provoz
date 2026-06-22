import streamlit as st
from github import Github

# --- KONFIGURÁCIA A PRIPOJENIE ---
# Tieto údaje budeme mať v "Secrets"
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"]) # Napr. "tvoje-meno/prevadzkove-hlasenia"
except Exception as e:
    st.error("Chyba pripojenia ku GitHubu. Skontrolujte Secrets.")

st.set_page_config(page_title="Hlásenie problémov", layout="centered")

# --- HLAVNÉ MENU (ZÁLOŽKY) ---
tab_report, tab_solver = st.tabs(["📢 Nahlásiť problém", "🛠 Solver (Admin)"])

# --- ZÁLOŽKA 1: NAHLASOVANIE ---
with tab_report:
    st.header("Nový prevádzkový problém")
    
    with st.form("reporting_form", clear_on_submit=True):
        kategoria = st.selectbox(
            "O aký problém ide?",
            ["Autostore","Práva/Access", "Odbáčanie na zjazdy/stanice/Turning to shipping lanes/stations", "Vytvorenie lokácií/New locations", "Chyby aktivácie/Activation error", "Neprepisovanie stavov/Job states stucked","Iné/Others"]
        )
        nadpis = st.text_input("Stručný popis (napr. Nejde skener)")
        detail = st.text_area("Detailnejšie informácie")
        priorita = st.select_slider("Priorita", options=["Nízka", "Stredná", "Vysoká"])
        
        submit = st.form_submit_button("Odoslať nahlásenie")

    if submit:
        if not nadpis:
            st.warning("Prosím, zadaj aspoň stručný popis.")
        else:
            # Vytvorenie Issue na GitHube
            body_text = f"**Kategória:** {kategoria}\n**Priorita:** {priorita}\n\n**Detail:**\n{detail}"
            repo.create_issue(
                title=f"[{kategoria}] {nadpis}",
                body=body_text,
                labels=[kategoria, priorita]
            )
            st.success("Problém bol nahlásený. Ďakujeme!")
            st.balloons()

# --- ZÁLOŽKA 2: SOLVER (ADMIN) ---
with tab_solver:
    st.header("Administrácia a riešenie")
    
    password = st.text_input("Zadaj prístupové heslo", type="password")
    
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.subheader("Aktuálne otvorené problémy")
        
        # Načítanie otvorených issues
        issues = repo.get_issues(state='open')
        
        if issues.totalCount == 0:
            st.info("Momentálne nie sú nahlásené žiadne problémy. Dobrá práca!")
        
        for issue in issues:
            with st.expander(f"#{issue.number}: {issue.title}"):
                st.write(issue.body)
                st.write(f"*Nahlásené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}*")
                
                # Tlačidlo na vyriešenie
                if st.button(f"Označiť ako VYRIEŠENÉ", key=f"close_{issue.number}"):
                    issue.create_comment("Problém bol vyriešený cez Solver appku.")
                    issue.edit(state='closed')
                    st.success(f"Problém #{issue.number} uzavretý!")
                    st.rerun()
    elif password != "":
        st.error("Nesprávne heslo!")
