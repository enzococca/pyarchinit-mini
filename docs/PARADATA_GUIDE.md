# Paradata Guide

Paradata are metadata about your archaeological data — authorship, licensing,
embargoes, external documents, and chronological epochs. They live alongside
your stratigraphic data and travel with it when you publish or import a graph.

## The 5 paradata node types

### AuthorNode (`/paradata/<site>/authors`)
A person who contributed to documenting the site.
Fields: **name** (required), optional **orcid**.

### LicenseNode (`/paradata/<site>/licenses`)
A license under which the site's data is published.
Fields: **name** (required), optional **url**.

### EmbargoNode (`/paradata/<site>/embargoes`)
A time-bound restriction on data publication.
Fields: **label** (required), optional **until** date.

### DocumentNode (`/paradata/<site>/documents`)
An external document (excavation report, photo album).
Fields: **title** (required), optional **uri**.

### EpochNode (`/paradata/<site>/epochs`)
A chronological period.
Fields: **name** (required), optional **start** / **end** years (negative for BCE).

## Storage

Paradata live in a JSON sidecar:
```
data/paradata/<site_slug>/paradata.json
```
This file IS committed to git — safe to edit by hand for bulk operations
(back up first).

The neighbouring `paradata.graphml` is a structural placeholder produced by
s3dgraphy; the actual paradata entities are in the JSON sidecar because
s3dgraphy 0.1.42's GraphML exporter does not round-trip standalone
paradata nodes.

When you save a US/USM record, the system auto-regenerates the merged
stratigraphic graph:
```
data/paradata/<site_slug>/stratigraphy.graphml
```
This file is NOT committed (derived artifact).

## Concurrent edits

Spec 2 policy: **last-writer-wins**. If two users edit the same AuthorNode
at the same time, the later save overwrites. Real-time conflict resolution
arrives in Spec 3.

## Adding a new paradata type

The 5 types are hardcoded into ParadataStore. Adding a 6th requires:
1. Add `_<KIND>_KEY` / `_<KIND>_PREFIX` constants
2. Add `list_<kind>` / `add_<kind>` / `update_<kind>` / `delete_<kind>` methods
3. Register the kind in `paradata_routes.KIND_METHODS` and `paradata_ui_routes.KIND_DEF`

See `docs/superpowers/specs/2026-05-17-spec-2-local-graph-paradata-design.md`
for the architecture.
