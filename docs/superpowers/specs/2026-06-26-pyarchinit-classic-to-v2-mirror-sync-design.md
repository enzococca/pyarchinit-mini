# Sync mirror unidirezionale `pyarchinit` (classico) → `pyarchinit_v2` (mini)

- **Data:** 2026-06-26
- **Stato:** design approvato, in attesa di piano di implementazione
- **Server:** Adarte (`ganesh@10.0.1.13`), Postgres su `10.0.1.6:5432`

## 1. Contesto e problema

Sul Postgres di Adarte coesistono due database:

- **`pyarchinit`** — schema PyArchInit classico, scritto da QGIS/desktop. **Unica sorgente di scrittura** dei dati archeologici.
- **`pyarchinit_v2`** — schema pyarchinit-mini, usato dall'app web (porta 5001) in **sola consultazione**. Contiene una **copia nativa** dei dati del classico, più tabelle proprie (derivate/calcolate).

Oggi **non esiste alcun meccanismo di sincronizzazione automatica** classico→v2 (verificato: nessun trigger cross-DB, nessuna funzione dblink/fdw custom, nessun cron, nessuno script, nessun codice nel repo). Esiste solo l'infrastruttura di sola lettura `postgres_fdw` (foreign server `pyarchinit_v1` → `pyarchinit`, schema `v1` con ~139 foreign table) ma non è usata per copiare dati. Un sync è stato fatto manualmente in passato, quindi i due DB sono quasi allineati ma il classico ha accumulato modifiche non propagate.

**Obiettivo:** quando in `pyarchinit` si inserisce / modifica / cancella qualcosa, `pyarchinit_v2` deve aggiornarsi di conseguenza, **automaticamente**.

## 2. Fatti accertati (evidenze)

- **Chiavi primarie preservate 1:1** tra classico e v2: `site_table.id_sito` identico su 1915/1915 (max id 1977=1977), `us_table.id_us` su 12546/12546 (max 30893=30893), `inventario_materiali_table.id_invmat` su 3233/3233 (max 5075=5075). → si può fare diff/upsert/delete **keyed sulla PK** in modo generico.
- **Tabelle mirrorate:** 128 presenti in entrambi i `public`, 107 con dati nel classico. Le più grandi sono layer GIS/catastali: `fano_2000_unione` 3.149.285 righe, `ctr_provincia_pesaro_urbino_epsg3004` 298.467, `fano_500_centro_storico` 267.231, `pyunitastratigrafiche` 183.164, ecc. **Sono già popolate e allineate in v2** (nessun caricamento iniziale enorme).
- **PostGIS 3.4.0 installato su entrambi** i DB. Colonne geometriche presenti (`the_geom`, `wkb_geometry`).
- **Divergenze attuali** (classico più recente, da riallineare al primo run):
  - `site_table`: 8/1915 righe con `descrizione`/`definizione_sito`/`sito_path` aggiornati nel classico.
  - `us_table`: 24 righe (Ravenna Rocca Brancaleone) con `rapporti` presenti nel classico e `'[]'` in v2. (`datazione` allineata.)
  - `pyunitastratigrafiche`: v2 ha +3 righe (effetto del trigger `create_geom`).
  - **Falso positivo:** `cont_per` (985) e `order_layer` (825) risultano "diversi" solo perché **il mini li calcola** e il classico li ha vuoti → NON vanno sovrascritti.
- **Tabelle solo-v2** (NON mirrorate, fuori scope): `tma_materiali_archeologici`, `tma_materiali_ripetibili`, `period_table`, `datazioni_table`, `harris_matrix_table`, `us_relationships_table`, `ai_conversations`, `ai_messages`, `users`, `pyarchinit_users`, `app_settings`, `thesaurus_category/field`, ecc.
- **Trigger esistenti in v2** che scatteranno sulle scritture del sync (comportamento atteso): `create_geom` (genera `pyunitastratigrafiche` su INSERT/UPDATE di US), `trg_sync_*` (users↔pyarchinit_users, thesaurus→nome campo).
- **Tabella senza PK:** `shape_finali_polygon` (8744 righe).

## 3. Requisiti (decisi con l'utente)

1. **Direzione:** solo `pyarchinit` → `pyarchinit_v2`. Il classico è l'unico writer; v2 è consultazione. Nessuna scrittura verso il classico.
2. **Freschezza:** schedulato **notturno** (no real-time). Il DB classico **non va toccato** (niente trigger su di esso, per non rischiare QGIS).
3. **Ambito:** **tutte** le tabelle mirrorate (archeologiche + layer GIS), perché servono sia al web mini sia a pyarchinit. Escluse: tabelle di sistema PostGIS e tabelle solo-v2.
4. **Operazioni:** INSERT, UPDATE, **DELETE attivo** (cancellazioni nel classico → rimosse da v2).
5. **Un solo motore:** il "re-sync" di adesso è semplicemente la prima esecuzione del motore (niente script separato — DRY).
6. **Cron:** 01:00 notturno (prima del backup `gestione_adarte` delle 02:00).

## 4. Non-obiettivi (YAGNI)

- Niente sincronizzazione real-time / trigger sul DB classico.
- Niente sincronizzazione bidirezionale o risoluzione conflitti (v2 non è scritto).
- Niente sync delle tabelle solo-v2 o di sistema PostGIS.
- Niente UI nel web per il sync (è un job di backend).

## 5. Architettura

**Un unico motore Python** (`scripts/sync_classic_to_v2.py` nel repo, eseguito sul server Adarte), guidato da configurazione. Due connessioni dirette `psycopg2`:

- **source** = `pyarchinit` (classico)
- **target** = `pyarchinit_v2` (mini)

(admin_pyarchinit ha accesso a entrambi; il server Adarte raggiunge `10.0.1.6`.) Non si usa il ponte FDW: connessione diretta più semplice e la logica di trasformazione vive in un unico posto.

### 5.1 Discovery delle tabelle

All'avvio il motore calcola l'insieme da sincronizzare:

```
mirrored = (public BASE TABLE in source)  ∩  (public BASE TABLE in target)
escludi  = tabelle di sistema PostGIS in public {spatial_ref_sys, raster_columns,
           raster_overviews}  (geometry_columns/geography_columns sono VIEW, già
           fuori dal filtro BASE TABLE; le tabelle topology stanno nello schema
           `topology`, non in public)
           + eventuali esclusioni esplicite da config
```

⚠️ **NON** escludere `public.layer`: è una vera tabella dati di pyarchinit (ha i trigger `layer_integrity_checks`), da non confondere con `topology.layer`. Le tabelle solo-v2 sono automaticamente fuori (non sono in `source`). Override per-tabella nel file di config (vedi §5.6).

### 5.2 Algoritmo per tabella (keyed sulla PK)

La **modalità** di ogni tabella deriva dalla dimensione (euristica) o da config:

- **`full`** (default per tabelle "dato", sotto soglia ~200k righe): **fa sempre il diff** (niente signature-gate, perché il gate `count+max(pk)` NON rileverebbe le modifiche in-place — es. gli 8 siti aggiornati hanno stesso conteggio e stesso max id). Carica `(pk, hash_riga)` da entrambi i lati e applica:
  - **INSERT**: pk nel classico assenti in v2.
  - **UPDATE**: pk comuni con `hash_riga` diverso → aggiorna **solo le colonne possedute dal classico**.
  - **DELETE**: pk in v2 assenti dal classico.
- **`keyset`** (tabelle enormi sopra soglia, senza colonna di modifica affidabile): prima un **signature-gate** economico = `count(*)` + `max(pk)` (persistito in `sync_state`); se invariato → **salta** la tabella (zero lavoro: i layer statici non costano nulla). Se cambiato → diff **solo sull'insieme delle PK** → INSERT dei nuovi id, DELETE degli id spariti. Le modifiche in-place di righe esistenti su questi layer statici sono rare; vengono recuperate dal **refresh completo periodico** (vedi §5.5).
- **`replace`** (tabelle senza PK, es. `shape_finali_polygon`): signature-gate `count(*)`; se cambiato, **TRUNCATE + copia integrale** dal classico.

`hash_riga` (modalità `full`) e firma (`keyset`/`replace`) vengono aggiornati in `sync_state` a fine tabella.

`hash_riga` = `md5` della concatenazione (`||`) delle **colonne comuni dato** (escludendo PK volatili e colonne preservate), per evitare il limite di 100 argomenti di `concat_ws`.

### 5.3 Politica colonne

- **Colonne comuni** = intersezione dei nomi colonna tra source e target.
- **Colonne PRESERVATE (mai scritte dal classico, escluse da hash e da UPDATE):**
  - calcolate dal mini: `order_layer`, `cont_per`
  - identità/versione: `entity_uuid`, `node_uuid`, `version_number`
  - audit/tempo: `created_at`, `updated_at`, `last_modified_timestamp`, `last_modified_by`, `editing_since`, `editing_by`, `audit_trail`, `sync_status`
  - i18n: colonne `*_en`
  - **qualunque colonna presente in v2 ma non nel classico** (per definizione mini-only)
  - estendibile per-tabella da config
- **Su INSERT** le colonne mini obbligatorie NOT NULL senza default vengono riempite: `created_at`/`updated_at` = `now()`, `version_number` = 1, `entity_uuid` = uuid generato; le altre con `NULL`/default.

### 5.4 Trasformazione tipi

Riuso dell'approccio `expr()` del merge festos (`scratchpad/merge2.py`): per ogni colonna comune, cast del valore del classico al tipo della colonna v2, con coercizioni sicure:
- `varchar/text` → `integer/bigint/smallint` (solo se numerico, altrimenti NULL)
- `bigint/numeric` → `boolean` (0→false, else true)
- `varchar` → `date` (ISO + europee `DD/MM/YYYY`, `DD-MM-YYYY`)
- `text` → `varchar(n)` con troncamento a `n`
- `timestamp` → `timestamptz`, ecc.
- **geometry**: copiata come EWKB (rappresentazione hex restituita da psycopg2, reinserita as-is; stesso PostGIS/SRID su entrambi).

### 5.5 Refresh completo periodico

Per le tabelle in modalità `keyset` (layer enormi), un **refresh completo settimanale** (es. domenica notte) forza un diff `full` (o un re-confronto profondo) per recuperare eventuali modifiche in-place non rilevate dal diff sulle sole PK. Configurabile/disattivabile.

### 5.6 Configurazione

File di config (YAML/JSON) nel repo, con DSN presi da variabili d'ambiente (no segreti hardcoded nel repo):

```
source_dsn_env: PYARCHINIT_CLASSIC_DSN
target_dsn_env: DATABASE_URL            # pyarchinit_v2
size_threshold_keyset: 200000
exclude_tables: [spatial_ref_sys, raster_columns, raster_overviews]   # NON includere public.layer
preserve_columns_global: [order_layer, cont_per, entity_uuid, node_uuid, version_number,
                          created_at, updated_at, last_modified_timestamp, last_modified_by,
                          editing_since, editing_by, audit_trail, sync_status]
overrides:
  shape_finali_polygon: { mode: replace }
  # esempi: tabella -> { mode, extra_preserve, natural_key, skip }
weekly_full_refresh: true
delete_enabled: true
```

### 5.7 Stato persistente

Tabella `sync_state` in v2: `table_name`, `last_signature`, `last_run_at`, `rows_inserted/updated/deleted`, `last_mode`, `error`. Serve al signature-gate e al report.

## 6. Sicurezza e robustezza

- **Dry-run di default**: senza `--apply` il motore stampa solo "inserirei/aggiornerei/cancellerei N per tabella" e NON scrive. Si applica solo con `--apply`.
- **`pg_dump` di `pyarchinit_v2`** prima del primo `--apply` reale (e prima di ogni refresh settimanale).
- **Transazione per-tabella**: una tabella che fallisce fa rollback solo di sé e non blocca le altre; l'errore viene loggato in `sync_state.error`.
- **Isolamento dal classico**: solo SELECT sul classico; nessuna scrittura, nessun trigger, nessun lock prolungato.
- **Log + riepilogo finale** (per tabella: modalità, +ins/~upd/-del, durata, esito) su file (`~/sync_classic_to_v2.log`).
- **Idempotente**: rieseguibile senza effetti collaterali; un secondo run a vuoto non cambia nulla.
- **Filtro `--tables`** per eseguire su un sottoinsieme (utile per il re-sync mirato e il debug).

## 7. Scheduling

- Cron Adarte: `0 1 * * *` → run notturno con `--apply` e log.
- `0 1 * * 0` (domenica) → run con `--apply --full-refresh` per le tabelle `keyset`.
- DSN via env nel comando cron (il classico: `postgresql://admin_pyarchinit:…@10.0.1.6:5432/pyarchinit`; v2: quello già usato dall'app).

## 8. Primo utilizzo (re-sync di adesso)

1. `--dry-run` completo → revisione del diff atteso (gli ~8 siti + 24 US Ravenna + eventuale altro).
2. `pg_dump` di v2.
3. `--apply` (eventualmente con `--tables site_table,us_table,inventario_materiali_table` per partire mirato).
4. Verifica con gli stessi controlli di allineamento usati in fase di analisi (chiavi + hash colonne comuni).
5. Installazione del cron.

## 9. Rischi e mitigazioni

- **Trigger v2 che scattano sul sync** (`create_geom`, `trg_sync_*`): atteso; documentato; verificare che non causino errori in massa (il `create_geom` rigenera geometrie US). Mitigazione: transazione per-tabella + verifica conteggi post-run.
- **Schemi che divergono nel tempo** (colonne aggiunte/rimosse): il motore lavora sull'intersezione delle colonne e ignora le non comuni → robusto; le nuove colonne dato del classico vengono sincronizzate solo se esistono anche in v2.
- **Geometrie con SRID diverso**: ad oggi coerenti; se divergessero, il copy EWKB preserva l'SRID di origine — eventuale `ST_Transform` solo se necessario (non previsto ora).
- **Tabelle enormi**: protette dal signature-gate (saltate se invariate) e dalla modalità `keyset`.
- **Performance prima notte**: la maggior parte delle tabelle è già allineata → diff a vuoto; solo le poche divergenti scrivono.

## 10. Testing / verifica

- Test del motore in **dry-run** su un DB di prova (o sul reale con `--dry-run`) confrontando i conteggi attesi.
- Dopo `--apply`: rieseguire i controlli di allineamento (chiavi identiche, 0 diff sulle colonne dato comuni escluse le preservate).
- Test idempotenza: secondo run consecutivo → 0 scritture.
- Test DELETE: cancellare una riga di prova nel classico → sparisce in v2 al run successivo (su tabella/riga di test).
