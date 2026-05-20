# Heriverse Deployment Spec Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `~/Downloads/Deployment and Infrastructure Proposal for Heriverse.docx` into a structured Italian markdown spec at `docs/superpowers/specs/2026-05-20-heriverse-deployment.md`, used as input material for the future Heriverse-bidirectional brainstorming session.

**Architecture:** Pure documentation task. No code changes. Extract docx text, restructure into sections, list open questions, document infrastructure constraints that the future integration session must respect.

**Tech Stack:** None — just text editing.

**Independent** — no blockers, no dependencies.

**Spec reference:** [`docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md`](../specs/2026-05-20-s3dgraphy-bridge-design.md) Appendix 2.

---

## Task 1 — Extract docx text to plain text

- [ ] Run the extraction one-liner:
  ```bash
  cd /tmp && cp "/Users/enzo/Downloads/Deployment and Infrastructure Proposal for Heriverse.docx" heriverse.docx && \
  unzip -p heriverse.docx word/document.xml | python3 -c "
  import sys, re
  xml = sys.stdin.read()
  xml = re.sub(r'</w:p>', '\n\n', xml)
  text = re.sub(r'<[^>]+>', '', xml)
  text = re.sub(r'\n{3,}', '\n\n', text)
  print(text.strip())
  " > /tmp/heriverse-raw.txt
  ```
- [ ] Verify `/tmp/heriverse-raw.txt` exists and contains ~80-120 lines of readable text (run `wc -l /tmp/heriverse-raw.txt` and a `head -40`).
- [ ] Quickly scan the file to identify the 8 sections (numbered headings) and note any "TBD" / "we'd like to check" markers for later.
- [ ] **Commit** — nothing yet; the raw file is in `/tmp` and not under repo. No commit at this step.

## Task 2 — Create the spec file scaffold

- [ ] Create `docs/superpowers/specs/2026-05-20-heriverse-deployment.md` with a metadata header:
  - `# Heriverse Deployment Spec (Input for Brainstorming Session D)`
  - **Date:** 2026-05-20
  - **Author:** Enzo Cocca
  - **Spec ID:** spec-heriverse-deployment-2026-05-20
  - **Status:** `Input for future brainstorming` (NOT an approved technical spec; raw preparation material).
  - **Source:** link to the original docx (path resolved in Task 7).
  - **Scope:** Italian summary of Heriverse infra docx; serves as input for the bidirectional integration brainstorm (Task #7).
- [ ] Add 8 empty section placeholders matching the docx structure (use `## 1. Struttura del repository e gestione ambienti`, `## 2. Architettura Docker Compose`, `## 3. Strategia container registry`, `## 4. Identity management (Keycloak)`, `## 5. Dimensionamento infrastruttura`, `## 6. Accesso server e gestione`, `## 7. Pipeline CI/CD`, `## 8. DNS`).
- [ ] Add three trailing section placeholders: `## Open Questions`, `## Constraints for mini-desk integration`, `## Source docx access`.
- [ ] **Commit** — `docs(spec-heriverse): scaffold deployment spec (input for session D)`

## Task 3 — Populate sections 1-4 (Italian summary)

- [ ] Section 1 — Repository structure and environment management: summarize the GitLab repo `git.3dresearch.it/stratigraph/docker-heriverse.git` and the three-branch model (`production` su PSNC, `staging` su PSNC, `development` su CNR). Note chi gestisce ciascun ambiente.
- [ ] Section 2 — Docker Compose architecture: elencare i servizi (Heriverse Node.js frontend on ATON.js, Heriverse-server Node.js middleware, CouchDB, Keycloak, Caddy reverse proxy). Indicare il ruolo di ognuno e come si compongono nel `docker-compose.yml`.
- [ ] Section 3 — Container registry strategy: riportare le tre opzioni elencate nel docx (3DR GitLab / GitHub / PSNC) e segnalare che la scelta è TBD.
- [ ] Section 4 — Identity management (Keycloak): riassumere la richiesta di hosting su infrastruttura PSNC e la centralizzazione SSO.
- [ ] Ogni sezione cita la fonte (es. "Cfr. docx sezione 2, p. 2") e link al docx (vedi Task 7).
- [ ] **Commit** — `docs(spec-heriverse): populate sections 1-4 (repo/compose/registry/keycloak)`

## Task 4 — Populate sections 5-8 (Italian summary)

- [ ] Section 5 — Dimensionamento infrastruttura: ambiente di test (256 GB storage / 8 GB RAM / 4 core) vs produzione (2 TB / 32 GB / 12 core).
- [ ] Section 6 — Accesso server e gestione: riassumere lo scope SSH richiesto e i permessi admin per 3DR + CNR DevOps. Segnalare i punti TBD.
- [ ] Section 7 — Pipeline CI/CD: confermare GitLab Runner su CNR dev per staging; la strategia di deploy produzione è TBD.
- [ ] Section 8 — DNS: target `heriverse.stratigraph-eccch.eu` (prod) e `heriverse-staging.stratigraph-eccch.eu` (staging). Stato readiness DNS da chiarire.
- [ ] **Commit** — `docs(spec-heriverse): populate sections 5-8 (sizing/access/ci/dns)`

## Task 5 — Open Questions section

- [ ] Estrarre da `/tmp/heriverse-raw.txt` ogni marker `TBD`, `we'd like to check`, `to be discussed`, `open` o equivalenti.
- [ ] Listarli come bullet in `## Open Questions`, raggruppati per area:
  - Hosting Keycloak (su PSNC? altra infra?)
  - Scope SSH e permessi amministratore (3DR + CNR DevOps)
  - Strategia di deploy produzione (workflow CI/CD complete pipeline)
  - Scelta container registry (3DR GitLab / GitHub / PSNC)
  - Readiness DNS (`stratigraph-eccch.eu` zone già delegata?)
  - Qualsiasi altro TBD trovato nel docx.
- [ ] Ogni open question dichiara esplicitamente chi deve rispondere (utente / Emanuel / PSNC / CNR) e la deadline indicativa (prima di sessione D).
- [ ] **Commit** — `docs(spec-heriverse): add Open Questions section`

## Task 6 — Constraints for mini-desk integration section

- [ ] Documentare i vincoli tecnici che la futura sessione D di brainstorming bidirezionale dovrà rispettare:
  - **CouchDB** è lo storage lato Heriverse (non negoziabile per docx).
  - **Keycloak** è l'SSO centralizzato; mini-desk dovrà autenticarsi via OIDC verso Keycloak.
  - **Caddy** è il reverse proxy (TLS terminato qui, niente entry point alternativi).
  - **heriverse-server (Node.js)** è l'unico API entry consentito dall'esterno verso lo stack Heriverse — mini-desk non parla mai direttamente a CouchDB.
  - **DNS** `heriverse.stratigraph-eccch.eu` (prod) e `heriverse-staging.stratigraph-eccch.eu` (staging); CORS / origini consentite vanno coordinate.
- [ ] Per ciascun vincolo, segnare l'impatto sul futuro design bidirezionale (es. "mini-desk dovrà esporre un client OIDC registrato in Keycloak").
- [ ] **Commit** — `docs(spec-heriverse): add Constraints for mini-desk integration section`

## Task 7 — Source docx access (pick ONE option)

Scegliere durante l'esecuzione l'opzione preferita dall'utente, poi eseguire solo gli step relativi.

- [ ] **Option A — Copia in repo:**
  - `mkdir -p docs/superpowers/specs/heriverse-source/`
  - `cp "/Users/enzo/Downloads/Deployment and Infrastructure Proposal for Heriverse.docx" docs/superpowers/specs/heriverse-source/Heriverse-deployment-source.docx`
  - Se l'utente non vuole binari in repo: aggiungere `docs/superpowers/specs/heriverse-source/` a `.gitignore` (e in tal caso il file resta solo locale, ma il path è documentato).
  - In `## Source docx access` del nuovo spec, scrivere: `Copia locale: docs/superpowers/specs/heriverse-source/Heriverse-deployment-source.docx` (e se gitignorato, segnalarlo).
- [ ] **Option B — Solo link al path originale:**
  - Lasciare il docx in `~/Downloads/`.
  - In `## Source docx access` scrivere: `Sorgente locale (non versionata): /Users/enzo/Downloads/Deployment and Infrastructure Proposal for Heriverse.docx`.
- [ ] **Commit** — `docs(spec-heriverse): wire source docx access (Option A/B)`

---

## Self-Review Checklist

- [ ] Tutte e 8 le sezioni del docx sono riassunte in italiano nello spec.
- [ ] Sezione `## Open Questions` non vuota, ogni domanda con owner + deadline indicativa.
- [ ] Sezione `## Constraints for mini-desk integration` esplicita per CouchDB / Keycloak / Caddy / heriverse-server / DNS.
- [ ] Sorgente docx accessibile (Option A copia o Option B link) e documentata.
- [ ] Header metadata corretto (Date, Status `Input for future brainstorming`, Spec ID, Author).
- [ ] Nessuna implementazione di codice in questo plan (è puro spec extraction).
- [ ] Commit separati per scaffold / sezioni 1-4 / sezioni 5-8 / open questions / constraints / source.