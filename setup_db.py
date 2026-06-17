import pymongo
import urllib.parse
import os
from dotenv import load_dotenv

# --- 1. SETTINGS & DOTENV-LOAD ---
load_dotenv()
USERNAME = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")

# Sicheres URL-Encoding für Sonderzeichen im Passwort
escaped_username = urllib.parse.quote_plus(USERNAME)
escaped_password = urllib.parse.quote_plus(PASSWORD)
URI = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.ytqppqd.mongodb.net/catalysis_project?appName=Cluster0"

def setup_database():
    print("Verbinde mit MongoDB Atlas...")
    try:
        client = pymongo.MongoClient(URI)
        db = client["catalysis_project"]
        collection = db["compounds"]

        # Alte Daten löschen, um sauber zu starten
        collection.delete_many({})

        # --- 2. HOCHDETAILLIERTE FORSCHUNGSDATEN ---
        realistic_data = [
            {
                "compound_id": "UK_CAT_001",
                "metadata": {
                    "calculation_type": "Opt + Freq + NMR",
                    "software": "ORCA 5.0.3",
                    "method": "B3LYP",
                    "basis_set": "def2-TZVP",
                    "solvation": "CPCM(Water)",
                    "convergence_reached": True
                },
                "properties": {
                    "final_energy_hartree": -514.8329104,
                    "dipole_moment_debye": 2.14,
                    "zero_point_energy_kcal_mol": 85.2
                },
                "geometry": {
                    "num_atoms": 20,
                    "xyz_coordinates": [
                        {"element": "C", "x": 0.123, "y": -1.456, "z": 0.000},
                        {"element": "O", "x": 1.200, "y": -1.456, "z": 0.000},
                        {"element": "N", "x": -0.500, "y": 0.000, "z": 0.000},
                        {"element": "C", "x": -1.200, "y": 1.100, "z": -0.500}
                    ]
                },
                "spectra": {
                    "ir": {
                        "frequencies_cm_1": [1650.5, 3100.2, 3250.0],
                        "intensities_km_mol": [450.2, 12.4, 80.1]
                    },
                    "nmr": {
                        "1H_shifts_ppm": [2.1, 7.4, 7.8],
                        "13C_shifts_ppm": [24.5, 128.2, 168.5]
                    }
                },
                "ml_features": {
                    "smiles": "CC(=O)Nc1ccc(O)cc1",  # Paracetamol
                    "molecular_weight": 151.16
                }
            },
            {
                "compound_id": "UK_CAT_002",
                "metadata": {
                    "calculation_type": "Opt + Freq + NMR",
                    "software": "Gaussian 16",
                    "method": "M06-2X",
                    "basis_set": "6-311G(d,p)",
                    "solvation": "SMD(Toluene)",
                    "convergence_reached": True
                },
                "properties": {
                    "final_energy_hartree": -345.6712399,
                    "dipole_moment_debye": 3.12,
                    "zero_point_energy_kcal_mol": 72.4
                },
                "geometry": {
                    "num_atoms": 14,
                    "xyz_coordinates": [
                        {"element": "C", "x": -0.100, "y": 0.000, "z": -1.200},
                        {"element": "O", "x": 1.050, "y": 0.000, "z": 2.100}
                    ]
                },
                "spectra": {
                    "ir": {
                        "frequencies_cm_1": [1705.4, 2800.1, 3050.8],
                        "intensities_km_mol": [520.1, 45.2, 15.0]
                    },
                    "nmr": {
                        "1H_shifts_ppm": [7.5, 7.6, 7.9, 10.0],
                        "13C_shifts_ppm": [128.5, 129.0, 134.5, 192.0]
                    }
                },
                "ml_features": {
                    "smiles": "O=Cc1ccccc1",  # Benzaldehyd
                    "molecular_weight": 106.12
                }
            },
            {
                "compound_id": "UK_CAT_003",
                "metadata": {
                    "calculation_type": "Opt + Freq",
                    "software": "ORCA 5.0.3",
                    "method": "wB97X-D3",
                    "basis_set": "def2-QZVPP",
                    "solvation": "None",
                    "convergence_reached": True
                },
                "properties": {
                    "final_energy_hartree": -248.1299441,
                    "dipole_moment_debye": 2.19,
                    "zero_point_energy_kcal_mol": 55.8
                },
                "geometry": {
                    "num_atoms": 11,
                    "xyz_coordinates": [
                        {"element": "N", "x": 0.000, "y": 0.000, "z": 1.400},
                        {"element": "C", "x": 0.000, "y": 1.140, "z": 0.700}
                    ]
                },
                "spectra": {
                    "ir": {
                        "frequencies_cm_1": [1450.0, 1580.5, 3020.1],
                        "intensities_km_mol": [15.4, 45.1, 20.2]
                    },
                    "nmr": {
                        "1H_shifts_ppm": [7.3, 7.7, 8.6],
                        "13C_shifts_ppm": [123.5, 135.8, 149.5]
                    }
                },
                "ml_features": {
                    "smiles": "c1ccncc1",  # Pyridin
                    "molecular_weight": 79.10
                }
            }
        ]
        
        collection.insert_many(realistic_data)
        print("✅ Erfolgreich! 3 realistische, hochdetaillierte Forschungsdatensätze wurden in die Cloud geladen.")
        
    except Exception as e:
        print(f"❌ Fehler bei der Verbindung: {e}")

if __name__ == "__main__":
    setup_database()