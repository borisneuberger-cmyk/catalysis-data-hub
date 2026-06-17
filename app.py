# --- 1. INITIALIZATION ---
st.set_page_config(
    page_title="Catalysis Data Hub",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Datenbank-Verbindung: Cloud (Streamlit Secrets) vs. Lokal (.env)
load_dotenv()

try:
    # Versuch 1: Streamlit Cloud Secrets
    USERNAME = st.secrets["DB_USER"]
    PASSWORD = st.secrets["DB_PASS"]
except Exception:
    # Versuch 2: Lokale .env Datei
    USERNAME = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASS")

# Sicherheits-Check, damit die App nicht mehr hart abstürzt, falls Passwörter fehlen
if not USERNAME or not PASSWORD:
    st.error("🚨 Datenbank-Zugangsdaten fehlen! Bitte in den Streamlit 'Advanced Settings' unter 'Secrets' eintragen.")
    st.stop()

@st.cache_resource
def get_database():
    escaped_user = urllib.parse.quote_plus(USERNAME)
    escaped_pass = urllib.parse.quote_plus(PASSWORD)
    uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.ytqppqd.mongodb.net/catalysis_project?appName=Cluster0"
    client = pymongo.MongoClient(uri)
    return client["catalysis_project"]

db = get_database()

# --- 2. SIDEBAR: QUERY PARAMETERS ---
with st.sidebar:
    st.title("⚙️ Query Parameters")
    st.markdown("Refine your database search criteria")
    st.divider()

    method_options = ["All", "B3LYP", "M06-2X", "wB97X-D3"]
    selected_method = st.selectbox("Computational Method", method_options)

    mw_range = st.slider("Molecular Weight (g/mol)", 50.0, 300.0, (70.0, 200.0))
    min_ir = st.slider("Min. IR Frequency (cm⁻¹)", 1000, 3500, 1400)
    min_dipole = st.slider("Min. Dipole Moment (Debye)", 0.0, 5.0, 0.0, step=0.1)
    
    # NMR Filter (13C Chemical Shifts)
    nmr_range = st.slider("13C NMR Chemical Shift (ppm)", 0.0, 220.0, (0.0, 220.0), step=1.0)

    st.divider()
    search_triggered = st.button("Execute Database Query", use_container_width=True, type="primary")

# --- 3. MAIN DASHBOARD ---
st.title("Catalysis Data Management System")
st.subheader("Team 1 | MVP Release: FAIR Data Retrieval")
st.divider()

if not search_triggered:
    c1, c2, c3 = st.columns(3)
    c1.metric("Cloud Status", "Online", "Connected via Atlas")
    c2.metric("Dataset Size", "2,000 Target", "High-Fidelity Data")
    c3.metric("Storage Architecture", "AWS / MongoDB", "Hybrid Data Lake")
    
    st.info("Welcome to the dashboard. Please utilize the parameters in the sidebar to retrieve computational data.")

else:
    # --- 4. LOGIC: DYNAMIC MONGODB QUERY ---
    query = {}
    
    if selected_method != "All":
        query["metadata.method"] = selected_method
        
    query["ml_features.molecular_weight"] = {"$gte": mw_range[0], "$lte": mw_range[1]}
    query["spectra.ir.frequencies_cm_1"] = {"$gte": min_ir}
    query["properties.dipole_moment_debye"] = {"$gte": min_dipole}
    query["spectra.nmr.13C_shifts_ppm"] = {"$gte": nmr_range[0], "$lte": nmr_range[1]}

    results = list(db.compounds.find(query, {"_id": 0}))

    if results:
        st.success(f"Query successful. Retrieved {len(results)} molecular records.")
        
        tab1, tab2, tab3 = st.tabs(["📊 Results Dataframe", "🖼️ Structural Analysis", "🛠️ Raw JSON Payload"])

        with tab1:
            df = pd.DataFrame([
                {
                    "Compound ID": r["compound_id"],
                    "Method": r["metadata"]["method"],
                    "MW (g/mol)": r["ml_features"]["molecular_weight"],
                    "Dipole (Debye)": r["properties"]["dipole_moment_debye"],
                    "IR Peaks (cm⁻¹)": r["spectra"]["ir"]["frequencies_cm_1"],
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
            st.write("Complete document payload from MongoDB (FAIR structure):")
            st.json(results[0])

        # --- 5. S3 DOWNLOAD SECTION ---
        st.divider()
        st.subheader("Raw Data Access (AWS S3 Object Storage)")
        col_s3_1, col_s3_2 = st.columns([3, 1])
        with col_s3_1:
            st.markdown(f"The raw computational log file for **{results[0]['compound_id']}** is available for secure download.")
        with col_s3_2:
            dummy_log = f"ORCA Output File\nID: {results[0]['compound_id']}\nEnergy: {results[0]['properties']['final_energy_hartree']}"
            st.download_button("Download Archive (S3)", dummy_log, file_name=f"{results[0]['compound_id']}_raw.out", use_container_width=True)

    else:
        st.warning("No records found matching the specified criteria. Please relax the query parameters.")