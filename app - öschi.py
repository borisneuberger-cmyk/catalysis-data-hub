import streamlit as st
import pymongo
import pandas as pd
import urllib.parse
import os
from dotenv import load_dotenv
from rdkit import Chem
from rdkit.Chem import Draw

# ==========================================
# 🔥 LACHNUMMER-SCHALTER FÜR ÖSTERREICH 🔥
# True = Vulgärer Schmäh | False = Seriöser Pitch-Modus
SCHMAE_MODE = True
# ==========================================

# --- 1. INITIALISIERUNG ---
st.set_page_config(
    page_title="Catalysis Data Hub" if not SCHMAE_MODE else "Molekül-Oasch-Katalog",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Datenbank-Verbindung (aus .env)
load_dotenv()
USERNAME = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")

@st.cache_resource
def get_database():
    escaped_user = urllib.parse.quote_plus(USERNAME)
    escaped_pass = urllib.parse.quote_plus(PASSWORD)
    uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.ytqppqd.mongodb.net/catalysis_project?appName=Cluster0"
    client = pymongo.MongoClient(uri)
    return client["catalysis_project"]

db = get_database()

# --- 2. SIDEBAR: MULTI-FILTER-MASKE ---
with st.sidebar:
    if SCHMAE_MODE:
        st.title("⚙️ Filter-Scheißdreck")
        st.markdown("Dreh an die Radln, sonst findst goa nix")
    else:
        st.title("⚙️ Search Filters")
        st.markdown("Verfeinern Sie die DB-Abfrage")
    st.divider()

    method_options = ["Alle", "B3LYP", "M06-2X", "wB97X-D3"] if not SCHMAE_MODE else ["Wurscht", "B3LYP", "M06-2X", "wB97X-D3"]
    
    label_method = "Quantenchemische Methode" if not SCHMAE_MODE else "Wos fia a Rechnerei?"
    selected_method = st.selectbox(label_method, method_options)
    if SCHMAE_MODE and selected_method == "Wurscht":
        selected_method = "Alle"

    label_mw = "Molekulargewicht (g/mol)" if not SCHMAE_MODE else "Fettheit vom Gfrast (g/mol)"
    mw_range = st.slider(label_mw, 50.0, 300.0, (70.0, 200.0))
    
    label_ir = "Min. IR-Frequenz (cm⁻¹)" if not SCHMAE_MODE else "Min. IR-Infrarot-Gejauchel (cm⁻¹)"
    min_ir = st.slider(label_ir, 1000, 3500, 1400)
    
    label_dipole = "Min. Dipolmoment (Debye)" if not SCHMAE_MODE else "Min. Dipol-Watsch'n (Debye)"
    min_dipole = st.slider(label_dipole, 0.0, 5.0, 0.0, step=0.1)
    
    label_nmr = "NMR Chem. Verschiebung (ppm)" if not SCHMAE_MODE else "NMR Atombussis Verschiebung (ppm)"
    nmr_range = st.slider(label_nmr, 0.0, 220.0, (0.0, 220.0), step=1.0)

    st.divider()
    btn_text = "Datenbank durchsuchen" if not SCHMAE_MODE else "🚀 Sauigln startn!"
    search_triggered = st.button(btn_text, use_container_width=True, type="primary")

# --- 3. HAUPTBEREICH: DASHBOARD ---
if SCHMAE_MODE:
    st.title("✨ Catalysis Oasch-Management System")
    st.subheader("Bande 1 | Schas-MVP: Daten ausm Orsch ziagn fia de KI")
else:
    st.title("Catalysis Data Management System")
    st.subheader("Team 1 | MVP Release: FAIR Data Retrieval")
st.divider()

if not search_triggered:
    c1, c2, c3 = st.columns(3)
    if SCHMAE_MODE:
        c1.metric("Cloud Status", "Rennt!", "Atlas is ned verreckt")
        c2.metric("Haufn an Daten", "2.000 Trümmer", "Ois do, oida")
        c3.metric("Bunker-Architektur", "AWS / MongoDB", "Mischmasch-Scheiß")
        st.info("Servas! Druck links aufn roten Knopp, sonst schimmelt de App do nua dumm rum.")
    else:
        c1.metric("Cloud Status", "Online", "Connected via Atlas")
        c2.metric("Dataset Size", "2.000 Target", "High-Fidelity Data")
        c3.metric("Storage Arch", "AWS / MongoDB", "Hybrid Data Lake")
        st.info("Willkommen im Dashboard! Bitte nutzen Sie die Parameter in der Seitenleiste, um Berechnungen abzurufen.")

else:
    # --- 4. LOGIK: DYNAMISCHE MONGODB QUERY ---
    query = {}
    
    if selected_method != "Alle":
        query["metadata.method"] = selected_method
        
    query["ml_features.molecular_weight"] = {"$gte": mw_range[0], "$lte": mw_range[1]}
    query["spectra.ir.frequencies_cm_1"] = {"$gte": min_ir}
    query["properties.dipole_moment_debye"] = {"$gte": min_dipole}
    query["spectra.nmr.13C_shifts_ppm"] = {"$gte": nmr_range[0], "$lte": nmr_range[1]}

    results = list(db.compounds.find(query, {"_id": 0}))

    if results:
        success_txt = f"Erfolgreich! {len(results)} Moleküle geladen." if not SCHMAE_MODE else f"Leiwand! {len(results)} Mistviecher ausm Netz g'fischt!"
        st.success(success_txt)
        
        tab_labels = ["📊 Ergebnis-Tabelle", "🖼️ Struktur-Analyse", "🛠️ Entwickler-JSON"] if not SCHMAE_MODE else ["📊 Datn-Haufn", "🖼️ Büdln fia de Augn", "🛠️ Nockads JSON fia de Nerds"]
        tab1, tab2, tab3 = st.tabs(tab_labels)

        with tab1:
            df = pd.DataFrame([
                {
                    "ID" if not SCHMAE_MODE else "Nummer": r["compound_id"],
                    "Method" if not SCHMAE_MODE else "Rechnung": r["metadata"]["method"],
                    "MW" if not SCHMAE_MODE else "Gewicht": r["ml_features"]["molecular_weight"],
                    "Dipole" if not SCHMAE_MODE else "Watsch'n": r["properties"]["dipole_moment_debye"],
                    "IR-Peaks": r["spectra"]["ir"]["frequencies_cm_1"],
                    "13C-NMR (ppm)": r["spectra"].get("nmr", {}).get("13C_shifts_ppm", [])
                } for r in results
            ])
            st.dataframe(df, use_container_width=True)

        with tab2:
            cols = st.columns(len(results))
            for i, r in enumerate(results):
                with cols[i]:
                    st.markdown(f"**{r['compound_id']}**")
                    mol = Chem.MolFromSmiles(r["ml_features"]["smiles"])
                    img = Draw.MolToImage(mol, size=(300, 300))
                    st.image(img, use_container_width=True)
                    st.caption(f"Method: {r['metadata']['method']}")

        with tab3:
            msg_json = "Vollständiges Dokument aus der MongoDB:" if not SCHMAE_MODE else "Do host dei gschissenes Dokument, du Einstein:"
            st.write(msg_json)
            st.json(results[0])

        # --- 5. S3 DOWNLOAD BEREICH ---
        st.divider()
        s3_title = "Raw Data Access (AWS S3 Object Storage)" if not SCHMAE_MODE else "Oide Log-Fetzn runtolodn (AWS S3)"
        st.subheader(s3_title)
        col_s3_1, col_s3_2 = st.columns([3, 1])
        with col_s3_1:
            msg_dl = f"Das vollständige Log-File für **{results[0]['compound_id']}** steht zum Download bereit." if not SCHMAE_MODE else f"Der gschissene ORCA-Schmoarn fia's Trumm **{results[0]['compound_id']}** liegt fixfertig do."
            st.markdown(msg_dl)
        with col_s3_2:
            dummy_log = f"ORCA Output File\nID: {results[0]['compound_id']}\nEnergy: {results[0]['properties']['final_energy_hartree']}"
            btn_dl = "S3 Download" if not SCHMAE_MODE else "💾 Gschlodder owasaugn"
            st.download_button(btn_dl, dummy_log, file_name="raw_output.out", use_container_width=True)

    else:
        err_txt = "Keine Ergebnisse gefunden. Bitte lockern Sie die Filter-Kriterien." if not SCHMAE_MODE else "Geh schei*n! Nix gfundn. Drah de Filter gscheider, du Heisl!"
        st.warning(err_txt)