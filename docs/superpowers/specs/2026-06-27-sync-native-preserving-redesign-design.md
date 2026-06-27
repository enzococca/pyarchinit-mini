# Redesign sync `pyarchinit` → `pyarchinit_v2`: preservare i dati nativi del v2

- **Data:** 2026-06-27
- **Stato:** design approvato, in attesa di piano di implementazione
- **Sostituisce** la logica di identità/DELETE del sync esistente (`pyarchinit_mini/sync/`, mergiato in `main` a `d78a605`).

## 1. Contesto e problema

Il sync attuale rispecchia `pyarchinit` (classico, v1) → `pyarchinit_v2` (mini, v2) usando la **chiave primaria** come identità: aggiorna/cancella le righe v2 in base alla presenza del loro id nel v1. In particolare **cancella ogni riga v2 il cui id non è presente nel v1**.

Due fatti rendono questo sbagliato per l'uso reale:

1. **Il v2 NON è di sola consultazione.** L'utente inserisce dati **nativi** direttamente nel v2 (potenzialmente in QUALSIASI tabella, "ovunque", inclusi i layer GIS). Questi dati **devono persistere** ai sync successivi. Il sync attuale li ha cancellati (557 righe: 544 `pyarchinit_thesaurus_sigle` + 10 `pyarchinit_quote` + 3 `pyarchinit_sondaggi`), poi ripristinate dal backup.
2. **v1 e v2 usano sequenze di id che si SOVRAPPONGONO.** Due righe diverse (una d'origine v1, una nativa v2) possono avere lo **stesso id** → la chiave surrogata NON è un'identità affidabile tra i due DB; un sync keyed sull'id sovrascriverebbe/cancellerebbe righe native.

**Obiettivo del redesign:** v1 → v2 a senso unico in cui:
- le modifiche/aggiunte/cancellazioni del **v1** si propagano al v2 **solo per le righe d'origine v1**;
- le righe **native del v2 non vengono mai cancellate né sovrascritte**;
- le collisioni di id sono gestite senza perdita di dati.

## 2. Modello d'identità: tabella di mappatura (provenance map)

Una tabella di servizio nel v2 fa da ponte d'identità tra id v1 e id v2:

```sql
CREATE TABLE public.sync_row_map (
    table_name  text NOT NULL,
    v1_pk       text NOT NULL,   -- valore PK lato v1 (testo; PK a colonna singola)
    v2_pk       text NOT NULL,   -- valore PK della riga corrispondente nel v2
    row_hash    text,            -- hash del contenuto sincronizzato (rilevamento modifiche)
    last_run_at timestamptz DEFAULT now(),
    PRIMARY KEY (table_name, v1_pk),
    UNIQUE (table_name, v2_pk)
);
```

Una riga compare in `sync_row_map` **se e solo se** è d'origine v1. Le righe native del v2 non sono mai mappate → sono invisibili al sync (mai update, mai delete).

## 3. Algoritmo per tabella

Per ogni tabella mirrorata con **PK a colonna singola** → modalità **`mapped`**. Tabelle **senza PK a colonna singola** (nessuna PK, o PK composita) → modalità **`additive`**. (Oggi l'unica senza PK a colonna singola è `shape_finali_polygon`.)

### 3.1 Bootstrap (auto, quando la mappa è vuota per la tabella)
Per ogni riga del v1 il cui `pk` **esiste anche come pk nel v2**, inserisci in `sync_row_map` la voce `(table, v1_pk, v2_pk = stesso valore, row_hash = hash corrente)`. Le righe v2 il cui pk **non** è presente nel v1 restano **fuori** dalla mappa = native. (Oggi è pulito: i nativi hanno id non presenti nel v1.) Il bootstrap è una tantum per tabella; per i layer GIS giganti è il costo pesante del primo giro.

### 3.2 Modalità `mapped`
1. (gate per tabelle grandi — §3.4)
2. Bootstrap se mappa vuota (§3.1).
3. Carica la mappa della tabella: `v1_pk → (v2_pk, row_hash)`.
4. Calcola dal v1: `v1_pk → coerced_hash` (hash sulle colonne-dato comuni, lato v1 con la **stessa coercizione** che verrebbe scritta — vedi §5). Carica l'insieme dei pk presenti nel v2.
5. Diff:
   - **INSERT**: `v1_pk` presente nel v1 ma non in mappa.
   - **UPDATE**: `v1_pk` in mappa e nel v1, con `coerced_hash` ≠ `row_hash` salvato (vince il v1). Se la riga v2 mappata non esiste più (cancellata a mano nel v2) → re-insert.
   - **DELETE**: `v1_pk` in mappa ma **non** nel v1 → cancella la riga v2 mappata e rimuovi la voce di mappa.
6. Applica (sul v2):
   - INSERT: scegli `v2_pk` → se `v1_pk` è **libero** nel v2 riusalo; se è **occupato** da una riga (nativa) non mappata → assegna un id dall'**intervallo alto dedicato** (§4). Inserisci la riga v1 (valori coercizzati) + riempimento campi obbligatori mini (`created_at/updated_at=now()`, `version_number=1`, `entity_uuid/node_uuid=gen_random_uuid()` se presenti e non comuni). Registra la voce di mappa.
   - UPDATE: aggiorna **solo le colonne-dato comuni** della riga v2 mappata (valori coercizzati); aggiorna `row_hash` in mappa.
   - DELETE: come sopra.
7. Le righe v2 non mappate (native) **non** vengono mai considerate.

### 3.3 Modalità `additive` (tabelle senza PK, es. `shape_finali_polygon`)
Identità = hash dell'intera riga (colonne comuni). INSERT delle righe v1 il cui hash-riga **non** è già nel v2; **nessun update, nessun delete**. Le righe native restano. (Limite documentato: update/delete del v1 su tabelle senza PK non si propagano.)

### 3.4 Tabelle grandi (layer GIS, > soglia, es. 200k righe)
Modalità `mapped` con **signature-gate** su `count(*) + max(pk)` del **v1** (persistito in `sync_state`): se invariato dall'ultimo giro → **salta** (zero lavoro). Al primo giro `sync_state` è vuoto → non salta → bootstrap + diff completo (pesante una tantum). Le modifiche in-place sul v1 (stesso count+maxpk) sulle tabelle grandi statiche sono rare; recuperabili con un refresh completo periodico/manuale (svuotando `sync_state` per quella tabella).

## 4. Gestione collisioni id

Quando una riga v1 nuova ha un `pk` **già occupato** nel v2 da una riga non mappata (nativa), la riga importata riceve un `v2_pk` da un **intervallo alto dedicato**: `collision_id_base` (default **1_000_000_000**) — un id `>= GREATEST(collision_id_base, max(pk)+1)` per quella tabella, che il v1 non raggiungerà mai per dati archeologici. La mappa registra `v1_pk → v2_pk` (id diverso). Le relazioni pyarchinit restano valide perché vanno **per nome** (sito/us), non per id surrogato. Assunzione: PK intero con spazio sopra 1 miliardo (vero per tutte le tabelle in gioco).

## 5. Coercizione tipi e idempotenza

Riuso dell'`expr()`/coerced-hash esistente. **Aggiunta:** per le colonne sorgente di tipo `character` (bpchar, riempito di spazi) → `rtrim` degli spazi finali nella coercizione (gli spazi di padding del CHAR sono semanticamente insignificanti). Risolve la non-idempotenza nota di `pyarchinit_thesaurus_sigle.sigla` (classico `char(3)` `'A  '` vs v2 `varchar` `'A'`, ~74 update perpetui). L'hash lato v1 usa la **stessa** coercizione dei valori scritti, così v1 e v2 convergono e il secondo giro è `+0 ~0 -0`.

## 6. Semantica di update e ambito

- Per le righe **d'origine v1**, vince sempre il **v1** (sovrascrive eventuali modifiche fatte nel v2 su quelle righe).
- Le righe **native** del v2 non vengono mai toccate (né update né delete).
- Ambito: **tutte** le tabelle mirrorate (archeologiche + layer GIS giganti inclusi nella mappa). Esclusioni: solo tabelle di sistema PostGIS (`spatial_ref_sys`, `raster_columns`, `raster_overviews`) e tabelle solo-v2.

## 7. Cosa cambia nel codice (rispetto al sync esistente)

- **`sync/rowmap.py` (nuovo):** gestione `sync_row_map` — `ensure_map_table`, `bootstrap_table`, `load_map`, `record_insert/update/delete`.
- **`sync/engine.py` (riscrittura del cuore):** `sync_table` passa da modalità full/keyset/replace (keyed su PK) a **`mapped`** (piccole = diff completo; grandi = gate) e **`additive`** (senza PK). DELETE solo sulle voci di mappa sparite dal v1. Inserimento con scelta `v2_pk` (riuso o intervallo alto).
- **`sync/transform.py`:** aggiunta `rtrim` per sorgenti `character` in `cast_expr` (§5).
- **`sync/config.py`:** nuovo `collision_id_base` (default 1_000_000_000); `exclude_tables` invariato; (niente `map_excluded` di default — si mappa tutto).
- **`sync/state.py`:** invariato, usato per il gate delle tabelle grandi.
- **`sync/policy.py`:** `select_mode` → ritorna `mapped`/`additive` (in base a presenza PK) + flag "gated" per dimensione.
- **Test:** riscrittura dei test del motore per il nuovo comportamento (preservazione native, collisione → intervallo alto, bootstrap, delete solo righe d'origine v1, idempotenza inclusa bpchar).

## 8. Sicurezza, migrazione, primo giro

- **Dry-run di default**, `--apply` per scrivere; transazione per-tabella con isolamento errori; `sync_state.error` registrato; log + riepilogo (invariati).
- **`pg_dump` del v2 prima del primo `--apply`** (backup attuale: `~/Downloads/pyarchinit_v2_pre_sync_20260626.dump`; rifarne uno aggiornato prima del re-apply).
- **Primo giro dopo il redesign:** il bootstrap semina la mappa dallo stato attuale (righe d'origine v1 già nel v2 con stesso id; native con id non-v1 escluse). Quindi il primo giro **non** ricancella i nativi (non mappati) e **non** re-inserisce le righe v1 (già mappate): risulterà quasi a zero, tranne la convergenza bpchar del thesaurus e le eventuali modifiche reali del v1 nel frattempo.
- ⚠️ Finché il redesign non è in produzione, **non rilanciare** il sync attuale (ricancellerebbe i nativi). Nessun cron attivo.

## 9. Casi particolari / limiti

- Riga d'origine v1 cancellata a mano nel v2 → re-inserita (v1 è la fonte per le sue righe).
- Tabelle senza PK → solo additivo (no propagazione di update/delete dal v1).
- Tabelle grandi → gate sul v1; modifiche in-place non rilevate dal gate fino a refresh.
- Collisione id → intervallo alto; assume PK intero con spazio sopra 1 miliardo.
- Il primo giro (bootstrap di tutte le mappe, ~4–4.5M voci inclusi i GIS) è pesante una tantum; le notti successive sono veloci.

## 10. Testing / verifica

- Unit: `cast_expr` bpchar rtrim; scelta `v2_pk` (riuso vs intervallo alto); diff mappato (insert/update/delete) come funzioni pure dove possibile.
- Integrazione (DB Postgres di test): bootstrap semina correttamente; riga nativa (pk non in v1) **mai** cancellata né toccata; riga d'origine v1 cancellata nel v1 → cancellata nel v2; collisione (v1 nuova con pk occupato da nativa) → nativa intatta + riga v1 inserita con id alto + mappa corretta; idempotenza (secondo giro `+0 ~0 -0`, inclusa una colonna bpchar e una a tipo divergente); tabella senza PK → additivo, native preservate.
- Post-apply su Adarte: ri-eseguire un dry-run → atteso ~0 (a parte modifiche v1 reali); verificare che le 557 native (thesaurus/quote/sondaggi) siano ancora presenti.
