import streamlit as st
from github import Github
import datetime
import math

# --- 1. KONFIGURÁCIA ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception:
    st.error("Chyba pripojenia ku GitHubu.")

@st.cache_data(ttl=60)
def get_issues_cached():
    # Načítame zoznam všetkých issues
    return list(repo.get_issues(state='all', sort='created', direction='desc'))

st.set_page_config(page_title="Issue Systém", layout="centered")

# --- HLAVIČKA ---
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("Issues Proces")
with col_refresh:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

tab1, tab2 = st.tabs(["📢 Nahlásiť Issue", "🔍 Sledovať stav"])

# --- 2. ZÁLOŽKA: NAHLASOVANIE (Nezmenená) ---
with tab1:
    st.header("Nové Issue")
    with st.form("reporting_form", clear_on_submit=True):
        st.subheader("Kontaktné údaje")
        c1, c2 = st.columns(2)
        with c1:
            meno = st.text_input("Meno / Login")
            oddelenie = st.text_input("Oddelenie")
        with c2:
            kontakt = st.text_input("T.č. / Kontakt")
        st.divider()
        st.subheader("Detail problému")
        kategoria = st.selectbox("Kategória", ["Autostore", "Práva/Access", "Odbáčanie na zjazdy/stanice", "Iné/Others"])
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
                body = f"### 👤 Kontakt\n- **Meno:** {meno if meno else 'Anonym'}\n- **Oddelenie:** {oddelenie if oddelenie else 'Neuvedené'}\n- **Kontakt:** {kontakt if kontakt else 'Neuvedené'}\n\n### 📝 Detail\n**Kategória:** {kategoria} | **Priorita:** {priorita}\n\n**Popis:**\n{detail}"
                if image_url: body += f"\n\n**Príloha:**\n![Foto]({image_url})"
                repo.create_issue(title=f"[{kategoria}] {nadpis}", body=body)
                st.cache_data.clear()
                st.success("✅ Nahlásené!")
                st.balloons()
            except Exception as e:
                st.error(f"Chyba: {e}")

# --- 3. ZÁLOŽKA: SLEDOVANIE (S FILTROM) ---
with tab2:
    st.header("Stav nahlásených vecí")
    
    # Checkbox pre filter
    show_resolved = st.checkbox("Zobraziť aj vyriešené (archív)", value=False)
    
    # Načítame základný zoznam
    all_issues = get_issues_cached()

    # FILTROVANIE DÁT
    if show_resolved:
        filtered_issues = all_issues
    else:
        # Ponecháme len tie, ktoré sú v stave 'open'
        filtered_issues = [i for i in all_issues if i.state == 'open']

    if not filtered_issues:
        st.info("Momentálne nie sú nahlásené žiadne otvorené problémy.")
    else:
        # Stránkovanie
        issues_per_page = 10
        total_pages = math.ceil(len(filtered_issues) / issues_per_page)
        
        # Ošetrenie, aby sme neboli na strane, ktorá už neexistuje po odfiltrovaní
        if 'current_page' not in st.session_state or st.session_state.current_page > total_pages:
            st.session_state.current_page = 1

        cp = st.session_state.current_page
        start_idx = (cp - 1) * issues_per_page
        current_batch = filtered_issues[start_idx : start_idx + issues_per_page]

        # Navigácia (len ak je viac ako 1 strana)
        if total_pages > 1:
            col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
            with col_p1:
                if st.button("⬅️") and cp > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
            with col_p2:
                st.write(f"Strana {cp} / {total_pages}")
            with col_p3:
                if st.button("➡️") and cp < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()

        st.divider()

        # Zobrazenie vyfiltrovaných issues
        for issue in current_batch:
            status = "🟠" if issue.state == "open" else "✅"
            with st.expander(f"{status} #{issue.number}: {issue.title}"):
                st.markdown(issue.body)
                st.caption(f"Vytvorené: {issue.created_at.strftime('%d.%m.%Y %H:%M')}")
                
                st.write("---")
                show_comments = st.checkbox("Zobraziť aktualizácie", key=f"check_{issue.number}")
                
                if show_comments:
                    with st.spinner("Sťahujem aktualizácie..."):
                        comments = list(issue.get_comments())
                        if comments:
                            for c in comments:
                                st.info(c.body)
                        else:
                            st.write("Zatiaľ žiadne aktualizácie.")
