import streamlit as st
from github import Github
import datetime
import math

# --- 1. KONFIGURÁCIA A CACHING ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia ku GitHubu.")

# Funkcia na načítanie dát s vyrovnávacou pamäťou (zostane v pamäti 60 sekúnd)
@st.cache_data(ttl=60)
def get_issues_cached(state='all'):
    # Získame všetky issues, prevedieme ich na list, aby sme s nimi vedeli pracovať
    return list(repo.get_issues(state=state, sort='created', direction='desc'))

@st.cache_data(ttl=60)
def get_comments_cached(issue_number):
    # Načítame komentáre pre konkrétne issue
    issue = repo.get_issue(number=issue_number)
    return list(issue.get_comments())

st.set_page_config(page_title="Issue Systém", layout="centered")

# --- HLAVIČKA ---
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("Issue Systém")
with col_refresh:
    if st.button("🔄 Refresh"):
        st.cache_data.clear() # Vymaže pamäť a vynúti nové načítanie
        st.rerun()

tab1, tab2 = st.tabs(["📢 Nahlásiť Issue", "🔍 Sledovať stav"])

# --- 2. ZÁLOŽKA: NAHLASOVANIE (Zostáva rovnaká) ---
with tab1:
    st.header("Nové Issue")
    with st.form("reporting_form", clear_on_submit=True):
        st.subheader("Kontaktné údaje")
        st.info("Kontaktné údaje nie sú povinné, ale je OK ich vyplniť.")
        c1, c2 = st.columns(2)
        with c1:
            meno = st.text_input("Meno / Login")
            oddelenie = st.text_input("Oddelenie")
        with c2:
            kontakt = st.text_input("T.č. / Kontakt")
        st.divider()
        st.subheader("Detail problému")
        kategoria = st.selectbox("O aký problém ide?", ["Autostore", "Práva/Access", "Odbáčanie na zjazdy/stanice", "Iné/Others"])
        nadpis = st.text_input("Stručný nadpis *")
        detail = st.text_area("Detailný popis *")
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
                txt_meno = meno if meno else "Anonymne"
                txt_oddelenie = oddelenie if oddelenie else "Neuvedené"
                txt_kontakt = kontakt if kontakt else "Neuvedené"
                body = f"### 👤 Kontakt\n- **Meno:** {txt_meno}\n- **Oddelenie:** {txt_oddelenie}\n- **Kontakt:** {txt_kontakt}\n\n### 📝 Detail\n**Kategória:** {kategoria} | **Priorita:** {priorita}\n\n**Popis:**\n{detail}"
                if image_url: body += f"\n\n**Príloha:**\n![Foto]({image_url})"
                repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body)
                st.cache_data.clear() # Vymažeme cache, aby sa nové issue hneď objavilo
                st.success("✅ Nahlásené!")
                st.balloons()
            except Exception as e:
                st.error(f"Chyba: {e}")

# --- 3. ZÁLOŽKA: SLEDOVANIE (STRÁNKOVANIE A RÝCHLOSŤ) ---
with tab2:
    st.header("Stav nahlásených vecí")
    
    # 1. Načítame všetky issues (z pamäte alebo z GitHubu)
    with st.spinner("Načítavam zoznam..."):
        all_issues = get_issues_cached()

    if not all_issues:
        st.info("Zatiaľ žiadne záznamy.")
    else:
        # --- LOGIKA STRÁNKOVANIA ---
        issues_per_page = 5 # Koľko issue uvidíme na jednej strane
        total_pages = math.ceil(len(all_issues) / issues_per_page)
        
        # Inicializácia čísla strany v pamäti prehliadača
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        # Ovládanie stránok (Tlačidlá Späť / Ďalej)
        col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
        with col_p1:
            if st.button("⬅️ Predchádzajúca") and st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
        with col_p2:
            st.write(f"Strana **{st.session_state.current_page}** z {total_pages}")
        with col_p3:
            if st.button("Nasledujúca ➡️") and st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()

        # Výpočet, ktoré issues zobraziť
        start_idx = (st.session_state.current_page - 1) * issues_per_page
        end_idx = start_idx + issues_per_page
        current_batch = all_issues[start_idx:end_idx]

        # Zobrazenie aktuálnej dávky
        for issue in current_batch:
            icon = "🟠" if issue.state == "open" else "✅"
            with st.expander(f"{icon} #{issue.number}: {issue.title}"):
                st.markdown(issue.body)
                st.caption(f"Vytvorené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
                st.divider()
                
                # Komentáre načítavame tiež cachovane pre rýchlosť
                comments = get_comments_cached(issue.number)
                if comments:
                    st.write("**Aktualizácie:**")
                    for comment in comments:
                        st.info(comment.body)
                else:
                    st.write("🕒 Čaká sa na vyjadrenie.")
