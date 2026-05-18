"""SwimlaneState — Cytoscape JSON <-> DB serialization.

Load: row_provider + us_table -> EditorState (Cytoscape-shaped).
Save: full impl in Task 11 (currently NotImplementedError).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .row_provider import Row, RowProvider
from .compound_layout import derive_row_id, initial_node_position
from .exceptions import SwimlaneStateError


@dataclass
class CytoscapeElement:
    data: dict
    classes: str = ""
    position: Optional[dict] = None


@dataclass
class EditorState:
    site: str
    rows: list
    nodes: list
    edges: list
    pending_changes: dict


@dataclass
class SaveResult:
    updated: int
    inserted: int
    deleted: int
    errors: tuple


class SwimlaneState:
    @staticmethod
    def load(session: Session, site: str) -> EditorState:
        """Load editor state for site. Empty state if site has no data."""
        # TODO(Spec-4): per-site period_table isolation. Currently period_table
        # is cross-site (any site sees all rows). When a user creates a row in
        # site A, it appears in site B's editor too. Add a `sito` column to
        # period_table with backward-compat migration if isolation becomes
        # load-bearing.
        provider = RowProvider(session, site)
        rows = provider.list_rows()

        # Resolve unit_type → fill_color via VocabProvider once per request so
        # the editor's `'background-color': data(color)` style renders properly.
        try:
            from pyarchinit_mini.vocab.provider import VocabProvider
            _vocab = VocabProvider.instance()
            _color_cache: dict[str, str] = {}

            def _color_for(ut: str) -> str:
                if ut in _color_cache:
                    return _color_cache[ut]
                try:
                    style = _vocab.get_visual_style(ut)
                    c = getattr(style, "fill_color", None) or "#CCCCCC"
                except Exception:
                    c = "#CCCCCC"
                _color_cache[ut] = c
                return c
        except Exception:
            def _color_for(ut: str) -> str:
                return "#CCCCCC"

        # Load US records for site
        us_rows = session.execute(text(
            "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid, "
            "periodo_iniziale, fase_iniziale "
            "FROM us_table WHERE sito = :sito ORDER BY id_us"
        ), {"sito": site}).fetchall()

        nodes: list[CytoscapeElement] = []
        us_num_to_node_id: dict[int, str] = {}
        row_counts: dict[str, int] = {}

        for r in us_rows:
            id_us = r[0]
            us_num = r[3]
            unita_tipo = r[4] or "US"
            periodo = r[7]
            fase = r[8]
            parent_row_id = derive_row_id(periodo, fase)

            node_id = f"us_{id_us}"
            us_num_to_node_id[us_num] = node_id

            idx = row_counts.get(parent_row_id, 0)
            row_counts[parent_row_id] = idx + 1

            # Build a minimal row-like object for initial_node_position
            class _RowLike:
                row_id = parent_row_id

            pos = initial_node_position(_RowLike(), idx)

            nodes.append(CytoscapeElement(
                data={
                    "id": node_id,
                    "label": f"{unita_tipo}{us_num}",
                    "parent": parent_row_id,
                    "unit_type": unita_tipo,
                    "color": _color_for(unita_tipo),
                    "period": periodo,
                    "phase": fase,
                    "us": us_num,
                    "node_uuid": r[6],
                },
                position=pos,
            ))

        # Add swimlane parent (compound) elements — one per row
        for row in rows:
            nodes.append(CytoscapeElement(
                data={
                    "id": row.row_id,
                    "label": _row_label(row),
                    "is_swimlane": True,
                    "color": row.color,
                    "period_name": row.period_name,
                    "phase_name": row.phase_name,
                },
                classes="swimlane",
            ))

        # Build edges from rapporti via EdgeRegistry
        edges = SwimlaneState._build_edges(us_rows, us_num_to_node_id)

        return EditorState(
            site=site,
            rows=rows,
            nodes=nodes,
            edges=edges,
            pending_changes={"us_updates": [], "us_inserts": [], "us_deletes": []},
        )

    @staticmethod
    def _build_edges(us_rows, us_num_to_node_id: dict) -> list[CytoscapeElement]:
        """Parse rapporti for each US via EdgeRegistry, deduplicating canonical
        triples ``(source, target, edge_name)``.

        pyarchinit stores stratigraphic relationships from both sides
        (``A copre B`` on row A AND ``B coperto da A`` on row B). Both tokens
        resolve to the same canonical edge ``A overlies B`` — without
        deduplication the editor renders the same arrow twice.

        Symmetric edge types (``has_same_time``) are deduped on the
        unordered pair so the bidirectional view doesn't show 2 lines.
        """
        try:
            from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry
            registry = EdgeRegistry()
        except Exception:
            return []

        # Edges where direction is meaningless (twins).
        SYMMETRIC = {"has_same_time"}
        # Edges that are inverses of each other (A overlies B ≡ B is_after A
        # in stratigraphic Harris semantics). When pyarchinit stores both
        # sides on different US rows, the editor must show one arrow, not two.
        INVERSE_PAIRS = {"overlies": "is_after", "is_after": "overlies"}

        edges: list[CytoscapeElement] = []
        edge_counter = 0
        seen: set[tuple] = set()

        for r in us_rows:
            us_num = r[3]
            rapporti = r[5] or ""
            if not rapporti.strip():
                continue
            source_node_id = us_num_to_node_id.get(us_num)
            if source_node_id is None:
                continue

            for token in rapporti.replace(";", ",").split(","):
                tok = token.strip()
                if not tok:
                    continue
                edge_name, target_us = registry.parse_rapporti_token(tok)
                if edge_name is None or target_us is None:
                    continue
                try:
                    target_int = int(target_us)
                except (ValueError, TypeError):
                    continue
                target_node_id = us_num_to_node_id.get(target_int)
                if target_node_id is None:
                    continue

                if edge_name in SYMMETRIC:
                    key = (edge_name, tuple(sorted((source_node_id, target_node_id))))
                else:
                    key = (edge_name, source_node_id, target_node_id)
                if key in seen:
                    continue
                # Check the inverse pair (overlies vs is_after) under the same
                # source/target pair — they represent the same edge.
                inverse_name = INVERSE_PAIRS.get(edge_name)
                if inverse_name is not None:
                    inverse_key = (inverse_name, target_node_id, source_node_id)
                    if inverse_key in seen:
                        continue
                seen.add(key)

                edge_counter += 1
                edges.append(CytoscapeElement(data={
                    "id": f"e{edge_counter}",
                    "source": source_node_id,
                    "target": target_node_id,
                    "label": edge_name,
                }))

        return edges

    @staticmethod
    def save(session: Session, site: str, state: dict) -> SaveResult:
        """Apply pending_changes to DB. Transaction-wrapped.

        Body:
          {
            "pending_us_updates": [{"us": int, "periodo_iniziale": str, "fase_iniziale": str}, ...],
            "pending_us_inserts": [{"sito", "us", "unita_tipo", "periodo_iniziale", "fase_iniziale", ...}, ...],
            "pending_us_deletes": [{"us": int}, ...],
          }

        After commit: triggers Spec 2 auto_regen for stratigraphy.graphml.
        """
        updates = state.get("pending_us_updates", [])
        inserts = state.get("pending_us_inserts", [])
        deletes = state.get("pending_us_deletes", [])

        updated = 0
        inserted = 0
        deleted = 0
        errors: list[str] = []

        try:
            for u in updates:
                try:
                    session.execute(text(
                        "UPDATE us_table SET periodo_iniziale=:p, fase_iniziale=:ph "
                        "WHERE us=:us AND sito=:sito"
                    ), {
                        "p": u.get("periodo_iniziale"),
                        "ph": u.get("fase_iniziale"),
                        "us": u["us"],
                        "sito": site,
                    })
                    updated += 1
                except Exception as e:
                    errors.append(f"update us={u.get('us')}: {e}")

            for ins in inserts:
                try:
                    node_uuid = ins.get("node_uuid")
                    if not node_uuid:
                        try:
                            from pyarchinit_mini.database.utils import generate_node_uuid
                            node_uuid = generate_node_uuid()
                        except Exception:
                            node_uuid = None
                    session.execute(text(
                        "INSERT INTO us_table (sito, area, us, unita_tipo, "
                        "periodo_iniziale, fase_iniziale, node_uuid) "
                        "VALUES (:sito, :area, :us, :ut, :p, :ph, :uuid)"
                    ), {
                        "sito": ins.get("sito", site),
                        "area": ins.get("area"),
                        "us": ins["us"],
                        "ut": ins.get("unita_tipo", "US"),
                        "p": ins.get("periodo_iniziale"),
                        "ph": ins.get("fase_iniziale"),
                        "uuid": node_uuid,
                    })
                    inserted += 1
                except Exception as e:
                    errors.append(f"insert us={ins.get('us')}: {e}")

            for d in deletes:
                try:
                    session.execute(text(
                        "DELETE FROM us_table WHERE us=:us AND sito=:sito"
                    ), {"us": d["us"], "sito": site})
                    deleted += 1
                except Exception as e:
                    errors.append(f"delete us={d.get('us')}: {e}")

            if errors:
                session.rollback()
                updated = inserted = deleted = 0
            else:
                session.commit()
                # Spec 2 auto-regen — best-effort
                try:
                    from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
                    _trigger_graph_regen(site, session=session)
                except Exception:
                    pass
        except Exception as e:
            session.rollback()
            raise SwimlaneStateError(f"save failed: {e}", op="save") from e

        return SaveResult(
            updated=updated,
            inserted=inserted,
            deleted=deleted,
            errors=tuple(errors),
        )


def _row_label(row: Row) -> str:
    if row.phase_name:
        return f"{row.period_name} / {row.phase_name}"
    return row.period_name
