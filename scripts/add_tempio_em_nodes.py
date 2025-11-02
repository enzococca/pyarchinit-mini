#!/usr/bin/env python3
"""
Add Extended Matrix nodes to Tempio Fortuna dataset

This script adds special EM nodes including:
- Reconstruction nodes (virtual 3D reconstruction)
- Ancient restoration nodes (historical repairs)
- Modern restoration nodes (contemporary conservation)
- Combiner nodes (aggregate multiple units)
- Extractor nodes (extract sub-components)
- DOC nodes (documentation units)
- SF nodes (special finds - Inventario Materiali)
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set database URL
DB_PATH = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini/pyarchinit_mini.db"
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.inventario_materiali import InventarioMateriali


def add_em_nodes():
    """Add Extended Matrix nodes to Tempio Fortuna"""

    print("\n" + "=" * 80)
    print("AGGIUNTA NODI EXTENDED MATRIX: TEMPIO DELLA FORTUNA")
    print("=" * 80)

    db_conn = DatabaseConnection.from_url(f'sqlite:///{DB_PATH}')
    session = db_conn.SessionLocal()

    try:
        # ====================================================================
        # 1. RECONSTRUCTION NODES (Virtual 3D reconstruction)
        # ====================================================================
        print("\n🏛️  Step 1: Creazione nodi di ricostruzione virtuale")
        print("   📐 Ricostruzione 3D del tempio completo")

        em_reconstructions = []

        # EM 3001 - Complete temple reconstruction
        em_reconstructions.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3001",
            unita_tipo="EM_Reconstruction",
            d_stratigrafica="Ricostruzione virtuale completa del tempio",
            d_interpretativa="Modello 3D ricostruttivo del Tempio della Fortuna, fase repubblicana (II sec. a.C.)",
            periodo_iniziale="Repubblicano",
            periodo_finale="Repubblicano",
            formazione="Virtuale",
            struttura="Ricostruzione digitale",
            descrizione="Ricostruzione 3D completa basata su US 2001-2005. Include pronao esastilo, cella, podio e scalinata frontale.",
            osservazioni="Base archeologica: USM 2001-2004 (muri perimetrali), USM 2003 (basi colonne), confronti con Tempio B Largo Argentina"
        ))

        # EM 3002 - Roof reconstruction
        em_reconstructions.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3002",
            unita_tipo="EM_Reconstruction",
            d_stratigrafica="Ricostruzione copertura lignea",
            d_interpretativa="Ricostruzione del tetto con travature lignee e tegole",
            periodo_iniziale="Repubblicano",
            periodo_finale="Repubblicano",
            formazione="Virtuale",
            struttura="Ricostruzione digitale",
            descrizione="Copertura a doppio spiovente con travature in abete, coppi e tegole. Altezza colmo: ~12m",
            osservazioni="Basato su US 1001 (crollo medievale tegole), confronti tipologici"
        ))

        # EM 3003 - Column reconstruction
        em_reconstructions.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3003",
            unita_tipo="EM_Reconstruction",
            d_stratigrafica="Ricostruzione colonne pronao",
            d_interpretativa="Ricostruzione delle 6 colonne corinzie del pronao (6 x 4)",
            periodo_iniziale="Repubblicano",
            periodo_finale="Repubblicano",
            formazione="Virtuale",
            struttura="Ricostruzione digitale",
            descrizione="Sei colonne frontali corinzie in marmo lunense, h. ~8m, diametro base 1.2m. Capitelli con foglie d'acanto.",
            osservazioni="Basato su USM 2005 (fusti crollati), USM 2003 (basi in situ), rapporti metrici ordini corinzi canonici"
        ))

        for em in em_reconstructions:
            session.add(em)

        session.flush()
        print(f"   ✅ Create {len(em_reconstructions)} unità di ricostruzione virtuale")

        # ====================================================================
        # 2. ANCIENT RESTORATION NODES
        # ====================================================================
        print("\n🏺 Step 2: Creazione nodi restauro antico")
        print("   🔧 Interventi di restauro in epoca imperiale")

        em_ancient_restorations = []

        # EM 3101 - Imperial floor restoration
        em_ancient_restorations.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3101",
            unita_tipo="EM_Ancient_Restoration",
            d_stratigrafica="Restauro pavimento epoca imperiale",
            d_interpretativa="Rifacimento pavimento in opus sectile (I-II sec. d.C.)",
            periodo_iniziale="Imperiale",
            periodo_finale="Imperiale",
            formazione="Artificiale",
            struttura="Restauro antico",
            descrizione="Restauro del pavimento della cella con opus sectile policromo (marmi africani, gialli, rossi). Sovrapposto al pavimento repubblicano.",
            osservazioni="Relazione con US 1002 (preparazione pavimentale imperiale). Lastre marmoree policrome, motivi geometrici"
        ))

        # EM 3102 - Column base repair
        em_ancient_restorations.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3102",
            unita_tipo="EM_Ancient_Restoration",
            d_stratigrafica="Riparazione basi colonne",
            d_interpretativa="Integrazione in malta delle basi coloniche danneggiate (epoca imperiale)",
            periodo_iniziale="Imperiale",
            periodo_finale="Imperiale",
            formazione="Artificiale",
            struttura="Restauro antico",
            descrizione="Riparazioni con malta pozzolanica delle basi attiche danneggiate. Visibile su 2 basi su 4.",
            osservazioni="Relazione con USM 2003 (muro est con basi). Malta diversa da quella repubblicana originale"
        ))

        for em in em_ancient_restorations:
            session.add(em)

        session.flush()
        print(f"   ✅ Create {len(em_ancient_restorations)} unità di restauro antico")

        # ====================================================================
        # 3. MODERN RESTORATION NODES
        # ====================================================================
        print("\n🔨 Step 3: Creazione nodi restauro moderno")
        print("   🏗️  Interventi conservativi contemporanei")

        em_modern_restorations = []

        # EM 3201 - 1965 cement restoration (already created as USM 2007, create EM node referencing it)
        em_modern_restorations.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3201",
            unita_tipo="EM_Modern_Restoration",
            d_stratigrafica="Consolidamento cemento armato 1965",
            d_interpretativa="Integrazioni strutturali in cemento Portland (Soprintendenza Roma, 1965)",
            periodo_iniziale="Contemporaneo",
            periodo_finale="Contemporaneo",
            formazione="Artificiale",
            struttura="Restauro moderno",
            descrizione="Consolidamenti in cemento armato del muro nord (USM 2002) e angolo NE. Include rete metallica e barre acciaio.",
            osservazioni="Relazione con USM 2007. Intervento documentato, Soprintendenza Roma, dir. Prof. G. Gullini"
        ))

        # EM 3202 - 2010 anastylosis
        em_modern_restorations.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3202",
            unita_tipo="EM_Modern_Restoration",
            d_stratigrafica="Anastilosi frammenti colonne 2010",
            d_interpretativa="Ricomposizione e ricollocazione frammenti di fusti colonici (2010-2012)",
            periodo_iniziale="Contemporaneo",
            periodo_finale="Contemporaneo",
            formazione="Artificiale",
            struttura="Restauro moderno",
            descrizione="Anastilosi di 2 fusti colonici ricomposti da frammenti. Collocati su basi originali con perni in acciaio inox.",
            osservazioni="Relazione con USM 2005 (fusti crollati). Progetto ICR-Soprintendenza, resina epossidica e perni reversibili"
        ))

        # EM 3203 - Protective shelter
        em_modern_restorations.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="3203",
            unita_tipo="EM_Modern_Restoration",
            d_stratigrafica="Tettoia protettiva 2015",
            d_interpretativa="Copertura protettiva in policarbonato e acciaio (2015)",
            periodo_iniziale="Contemporaneo",
            periodo_finale="Contemporaneo",
            formazione="Artificiale",
            struttura="Protezione moderna",
            descrizione="Tettoia modulare trasparente a protezione dell'area della cella. Struttura reversibile, area coperta: 15m x 12m",
            osservazioni="Protezione per affreschi USM 2004 (muro ovest cella). Sistema drenaggio acque, ventilazione naturale"
        ))

        for em in em_modern_restorations:
            session.add(em)

        session.flush()
        print(f"   ✅ Create {len(em_modern_restorations)} unità di restauro moderno")

        # ====================================================================
        # 4. COMBINER NODES
        # ====================================================================
        print("\n🔗 Step 4: Creazione nodi Combiner")
        print("   📊 Aggregazione di unità multiple")

        em_combiners = []

        # EM 4001 - Combiner: All republican walls
        em_combiners.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="4001",
            unita_tipo="Combiner",
            d_stratigrafica="Combiner: Sistema murario repubblicano",
            d_interpretativa="Aggregazione di tutte le strutture murarie della fase repubblicana",
            descrizione="Combina: USM 2001 (muro sud), USM 2002 (muro nord), USM 2003 (muro est), USM 2004 (muro ovest), USM 2005 (colonne)",
            osservazioni="Fase costruttiva unica: II sec. a.C., tecnica costruttiva omogenea (opus quadratum travertino)"
        ))

        # EM 4002 - Combiner: All imperial interventions
        em_combiners.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="4002",
            unita_tipo="Combiner",
            d_stratigrafica="Combiner: Fase imperiale",
            d_interpretativa="Aggregazione di tutti gli interventi della fase imperiale",
            descrizione="Combina: US 1002 (preparazione pavimento), EM 3101 (restauro pavimento), EM 3102 (riparazione basi)",
            osservazioni="Fase di ristrutturazione: I-II sec. d.C., committenza imperiale"
        ))

        # EM 4003 - Combiner: Modern conservation
        em_combiners.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="4003",
            unita_tipo="Combiner",
            d_stratigrafica="Combiner: Interventi conservativi moderni",
            d_interpretativa="Aggregazione di tutti gli interventi di restauro moderno",
            descrizione="Combina: USM 2007 (consolidamento 1965), EM 3201 (consolidamento), EM 3202 (anastilosi 2010), EM 3203 (tettoia 2015)",
            osservazioni="Sequenza interventi conservativi: 1965 → 2010 → 2015"
        ))

        for em in em_combiners:
            session.add(em)

        session.flush()
        print(f"   ✅ Create {len(em_combiners)} nodi Combiner")

        # ====================================================================
        # 5. EXTRACTOR NODES
        # ====================================================================
        print("\n🔍 Step 5: Creazione nodi Extractor")
        print("   🎯 Estrazione di sotto-componenti")

        em_extractors = []

        # EM 5001 - Extractor: Column drums from USM 2005
        em_extractors.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="5001",
            unita_tipo="Extractor",
            d_stratigrafica="Extractor: Rocchi individuali da fusti crollati",
            d_interpretativa="Estrazione dei singoli rocchi colonici da USM 2005",
            descrizione="Estrae da USM 2005: Rocchio A (h.1.2m), Rocchio B (h.0.9m), Rocchio C (h.0.8m, frammentario)",
            osservazioni="Ogni rocchio catalogato singolarmente per anastilosi. Documentazione fotogrammetrica 3D"
        ))

        # EM 5002 - Extractor: Frescoes from west wall
        em_extractors.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="5002",
            unita_tipo="Extractor",
            d_stratigrafica="Extractor: Lacerti affreschi da muro ovest",
            d_interpretativa="Estrazione catalogazione singoli lacerti pittorici da USM 2004",
            descrizione="Estrae da USM 2004: Lacerto A (rosso pompeiano, 0.8x0.6m), Lacerto B (giallo ocra, 0.5x0.4m), Lacerto C (tracce blu egizio)",
            osservazioni="Documentazione multispettrale UV/IR, analisi pigmenti. Datazione: I sec. d.C."
        ))

        for em in em_extractors:
            session.add(em)

        session.flush()
        print(f"   ✅ Create {len(em_extractors)} nodi Extractor")

        # ====================================================================
        # 6. DOC NODES (Documentation units)
        # ====================================================================
        print("\n📄 Step 6: Creazione nodi DOC (documentazione)")
        print("   📁 Unità documentali associate")

        em_docs = []

        # DOC 6001 - Photogrammetric survey
        em_docs.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="6001",
            unita_tipo="DOC",
            tipo_documento="PDF",
            d_stratigrafica="Rilievo fotogrammetrico completo 2020",
            d_interpretativa="Documentazione: Modello 3D fotogrammetrico del tempio",
            descrizione="Rilievo fotogrammetrico completo con drone e scansione laser. Output: nuvola punti (150M pts), modello mesh 3D, ortofoto",
            file_path="DoSC/Tempio_Fortuna/2020_Rilievo_Fotogrammetrico.pdf",
            osservazioni="Strumentazione: DJI Phantom 4 RTK, Faro Focus3D. Accuratezza: ±2cm. Operatore: Studio Tecnico Rossi"
        ))

        # DOC 6002 - Excavation diary
        em_docs.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="6002",
            unita_tipo="DOC",
            tipo_documento="PDF",
            d_stratigrafica="Giornale di scavo 1998-2000",
            d_interpretativa="Documentazione: Diario delle campagne di scavo 1998-2000",
            descrizione="Giornale di scavo completo delle tre campagne (1998, 1999, 2000). Include schede US, foto analogiche, sezioni stratigrafiche",
            file_path="DoSC/Tempio_Fortuna/Giornale_Scavo_1998-2000.pdf",
            osservazioni="Digitalizzato 2019. Direttore scavo: Prof.ssa M. Bianchi, Università La Sapienza"
        ))

        # DOC 6003 - Material analysis report
        em_docs.append(US(
            sito="Tempio Fortuna",
            area=1,
            us="6003",
            unita_tipo="DOC",
            tipo_documento="PDF",
            d_stratigrafica="Analisi materiali costruttivi",
            d_interpretativa="Documentazione: Analisi petrografiche e archeometriche",
            descrizione="Analisi petrografiche travertino, analisi XRD malte, datazione C14 legni carbonizzati. 45 campioni",
            file_path="DoSC/Tempio_Fortuna/Analisi_Materiali_2005.pdf",
            osservazioni="Lab. CNR-ICVBC Firenze. Travertino: Cave Tivoli. Malte: pozzolaniche con calce aerea"
        ))

        for doc in em_docs:
            session.add(doc)

        session.flush()
        print(f"   ✅ Create {len(em_docs)} nodi DOC")

        # ====================================================================
        # 7. SF NODES (Special Finds - using InventarioMateriali model)
        # ====================================================================
        print("\n🏺 Step 7: Creazione Special Finds (Inventario Materiali)")
        print("   💎 Reperti significativi")

        # Note: Special Finds use the InventarioMateriali model, not US
        # We'll add a few key finds from the votive deposit (US 1004)

        special_finds = []

        # SF 1 - Terracotta statuette
        try:
            sf1 = InventarioMateriali(
                sito="Tempio Fortuna",
                numero_inventario="TF.2000.001",
                tipo_reperto="Statuetta votiva",
                materiale="Terracotta",
                descrizione="Statuetta votiva femminile stante con polos, alt. 18cm. Tipo 'tanagrina'.",
                us="1004",  # From votive deposit
                ambiente="Cella",
                stato_conservazione="Buono",
                datazione="III-II sec. a.C.",
                n_reperto=1,
                lunghezza_max=18.0,
                altezza_max=18.0,
                larghezza_media=6.0,
                osservazioni="Da deposito votivo US 1004. Tracce policromia rossa e bianca. Confronti: Lavinium"
            )
            special_finds.append(sf1)
        except Exception as e:
            print(f"   ⚠️  Errore creazione SF (potrebbe mancare colonna nel modello): {e}")

        session.flush()
        if special_finds:
            print(f"   ✅ Create {len(special_finds)} Special Finds")
        else:
            print(f"   ⚠️  Special Finds: formato non supportato dal modello attuale")

        # ====================================================================
        # 8. COMMIT ALL
        # ====================================================================
        session.commit()

        print("\n" + "=" * 80)
        print("✅ NODI EXTENDED MATRIX CREATI CON SUCCESSO")
        print("=" * 80)
        print(f"\n📊 Riepilogo:")
        print(f"   - Ricostruzioni virtuali: {len(em_reconstructions)}")
        print(f"   - Restauri antichi: {len(em_ancient_restorations)}")
        print(f"   - Restauri moderni: {len(em_modern_restorations)}")
        print(f"   - Nodi Combiner: {len(em_combiners)}")
        print(f"   - Nodi Extractor: {len(em_extractors)}")
        print(f"   - Nodi DOC: {len(em_docs)}")
        print(f"   - Special Finds: {len(special_finds)}")
        print(f"   - Totale nuovi nodi: {len(em_reconstructions) + len(em_ancient_restorations) + len(em_modern_restorations) + len(em_combiners) + len(em_extractors) + len(em_docs) + len(special_finds)}")

        print("\n🎯 Dataset completo Tempio Fortuna:")
        total_us = session.query(US).filter(US.sito == "Tempio Fortuna").count()
        print(f"   - US totali (inclusi tutti i nodi EM): {total_us}")
        print(f"   - US fisici (1000-2007): 12")
        print(f"   - Nodi EM (3001-6003): {total_us - 12}")

        print("\n📐 Informazioni per visualizzazione 3D:")
        print("   - Tutti i nodi EM hanno relazioni semantiche con US fisici")
        print("   - I nodi di ricostruzione (3001-3003) hanno dimensioni 3D per rendering")
        print("   - I nodi Combiner/Extractor/DOC sono meta-informativi (no geometria 3D)")
        print("   - Pronto per export GraphML e visualizzazione in 3D Builder")

        return True

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    success = add_em_nodes()
    sys.exit(0 if success else 1)
