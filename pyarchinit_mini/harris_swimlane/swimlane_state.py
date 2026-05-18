"""SwimlaneState — Cytoscape JSON <-> DB serialization.

Load: row_provider + us_table -> EditorState (Cytoscape-shaped).
Save: full impl in Task 11 (currently NotImplementedError).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .row_provider import Row, RowProvider, PERIOD_COLORS
from .compound_layout import derive_row_id, initial_node_position
from .exceptions import SwimlaneStateError


_VALID_GROUP_BY = frozenset({
    "period_phase",
    "struttura", "attivita", "settore", "area",
    "ambient", "saggio", "quad_par",
    "none",
})

_DISTINCT_FIELD_COLS = {
    "struttura": "struttura",
    "attivita": "attivita",
    "settore": "settore",
    "area": "area",
    "ambient": "ambient",
    "saggio": "saggio",
    "quad_par": "quad_par",
}


def _build_lanes_by_distinct(session, site: str, col: str) -> list:
    """Return one Row per DISTINCT value of us_table.<col> for the site."""
    try:
        rows = session.execute(
            text(f"SELECT DISTINCT COALESCE({col}, '') AS v FROM us_table "
                 f"WHERE sito = :sito ORDER BY v"),
            {"sito": site},
        ).fetchall()
    except Exception:
        # Column doesn't exist in this DB schema — return single fallback lane
        rows = []

    out = []
    for i, r in enumerate(rows):
        value = r[0] or ""
        if not value:
            value = "(unset)"
        safe = value.lower().replace(" ", "_").replace("/", "_")
        row_id = "row_" + safe if safe else "row_unset"
        out.append(Row(
            row_id=row_id,
            period_name=value,
            phase_name=None,
            start_date=None,
            end_date=None,
            color=PERIOD_COLORS[i % len(PERIOD_COLORS)],
            source=f"distinct_{col}",
        ))
    if not out:
        out.append(Row(
            row_id="row_unset",
            period_name="(unset)",
            phase_name=None,
            start_date=None,
            end_date=None,
            color=PERIOD_COLORS[0],
            source=f"distinct_{col}",
        ))
    return out


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
    group_by: str = "period_phase"


@dataclass
class SaveResult:
    updated: int
    inserted: int
    deleted: int
    errors: tuple


class SwimlaneState:
    @staticmethod
    def load(session: Session, site: str, *, group_by: str = "period_phase") -> EditorState:
        """Load editor state for site, organised by group_by.

        group_by must be one of the 9 values in _VALID_GROUP_BY.
        Raises ValueError for unknown values.
        """
        if group_by not in _VALID_GROUP_BY:
            raise ValueError(f"invalid group_by: {group_by!r}")

        # TODO(Spec-4): per-site period_table isolation. Currently period_table
        # is cross-site (any site sees all rows). When a user creates a row in
        # site A, it appears in site B's editor too. Add a `sito` column to
        # period_table with backward-compat migration if isolation becomes
        # load-bearing.
        if group_by == "period_phase":
            provider = RowProvider(session, site)
            rows = provider.list_rows()
        elif group_by == "none":
            rows = [Row(
                row_id="row_default",
                period_name="All",
                phase_name=None,
                start_date=None,
                end_date=None,
                color=PERIOD_COLORS[0],
                source="virtual_none",
            )]
        else:
            col = _DISTINCT_FIELD_COLS[group_by]
            rows = _build_lanes_by_distinct(session, site, col)

        # Resolve unit_type → visual_style via VocabProvider once per request,
        # cached. The editor's Cytoscape style uses `data(color)` and
        # `data(shape)`; if either is missing the node renders grey rectangles
        # and Cytoscape logs a warning per node.
        _SHAPE_TO_CYTOSCAPE = {
            "rounded_rectangle": "roundrectangle",
            "parallelogram": "rhomboid",
            "trapezium": "triangle",
            "trapezium2": "vee",
            # Names that are already valid Cytoscape shapes pass through.
        }
        try:
            from pyarchinit_mini.vocab.provider import VocabProvider
            _vocab = VocabProvider.instance()
            _style_cache: dict[str, dict] = {}

            def _style_for(ut: str) -> dict:
                if ut in _style_cache:
                    return _style_cache[ut]
                try:
                    vs = _vocab.get_visual_style(ut)
                    raw_shape = (
                        vs.get("shape") if isinstance(vs, dict)
                        else getattr(vs, "shape", "rectangle")
                    )
                    fill = (
                        vs.get("fill_color") if isinstance(vs, dict)
                        else getattr(vs, "fill_color", None)
                    ) or "#CCCCCC"
                    border = (
                        vs.get("border_color") if isinstance(vs, dict)
                        else getattr(vs, "border_color", None)
                    ) or "#333333"
                    border_style = (
                        vs.get("border_style") if isinstance(vs, dict)
                        else getattr(vs, "border_style", None)
                    ) or "solid"
                    out = {
                        "color": fill,
                        "shape": _SHAPE_TO_CYTOSCAPE.get(raw_shape, raw_shape),
                        "border_color": border,
                        "border_style": border_style,
                    }
                except Exception:
                    out = {"color": "#CCCCCC", "shape": "rectangle",
                           "border_color": "#333333", "border_style": "solid"}
                _style_cache[ut] = out
                return out
        except Exception:
            def _style_for(ut: str) -> dict:
                return {"color": "#CCCCCC", "shape": "rectangle",
                        "border_color": "#333333", "border_style": "solid"}

        # Load US records for site.
        # Try extended SELECT (with distinct-field columns) first; fall back to
        # the base schema if those columns don't exist (older DB fixtures).
        _HAS_EXTRA_COLS = True
        try:
            us_rows = session.execute(text(
                "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid, "
                "periodo_iniziale, fase_iniziale, "
                "d_stratigrafica, datazione, file_path, "
                "struttura, attivita, settore, ambient, saggio, quad_par "
                "FROM us_table WHERE sito = :sito ORDER BY id_us"
            ), {"sito": site}).fetchall()
        except Exception:
            _HAS_EXTRA_COLS = False
            us_rows = session.execute(text(
                "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid, "
                "periodo_iniziale, fase_iniziale, "
                "d_stratigrafica, datazione, file_path "
                "FROM us_table WHERE sito = :sito ORDER BY id_us"
            ), {"sito": site}).fetchall()

        # Column index map for distinct-field group_by values (only valid when
        # _HAS_EXTRA_COLS is True).
        _col_index_map = {
            "area": 2, "struttura": 12, "attivita": 13, "settore": 14,
            "ambient": 15, "saggio": 16, "quad_par": 17,
        }

        def _parent_row_id_for(r) -> str:
            if group_by == "period_phase":
                return derive_row_id(r[7], r[8])  # periodo, fase
            if group_by == "none":
                return "row_default"
            if not _HAS_EXTRA_COLS:
                return "row_unset"
            idx = _col_index_map[group_by]
            raw = r[idx] or ""
            if not raw:
                return "row_unset"
            safe = raw.lower().replace(" ", "_").replace("/", "_")
            return "row_" + safe

        nodes: list[CytoscapeElement] = []
        us_num_to_node_id: dict[int, str] = {}
        row_counts: dict[str, int] = {}

        for r in us_rows:
            id_us = r[0]
            us_num = r[3]
            unita_tipo = r[4] or "US"
            periodo = r[7]
            fase = r[8]
            parent_row_id = _parent_row_id_for(r)

            node_id = f"us_{id_us}"
            us_num_to_node_id[us_num] = node_id

            idx = row_counts.get(parent_row_id, 0)
            row_counts[parent_row_id] = idx + 1

            # Build a minimal row-like object for initial_node_position
            class _RowLike:
                row_id = parent_row_id

            pos = initial_node_position(_RowLike(), idx)

            style = _style_for(unita_tipo)
            nodes.append(CytoscapeElement(
                data={
                    "id": node_id,
                    "label": f"{unita_tipo}{us_num}",
                    "parent": parent_row_id,
                    "unit_type": unita_tipo,
                    # Visual fields — read by harris_creator_editor.js Cytoscape style
                    "color": style["color"],
                    "shape": style["shape"],
                    "border_color": style["border_color"],
                    "border_style": style["border_style"],
                    # Identity + provenance
                    "us": us_num,
                    "us_number": us_num,          # Properties panel reads this name
                    "node_uuid": r[6],
                    # Temporal
                    "period": periodo,
                    "phase": fase,
                    # Descriptive fields the Properties panel populates
                    "description": r[9] or "",   # d_stratigrafica
                    "area": (r[2] or "") if r[2] is not None else "",
                    "datazione": r[10] or "",
                    "file_path": r[11] or "",
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

        # Build edges from rapporti (legacy text) AND us_relationships_table
        # (dedicated table — pyarchinit's primary store for relationships).
        edges = SwimlaneState._build_edges(us_rows, us_num_to_node_id)
        edges.extend(SwimlaneState._build_edges_from_relationships_table(
            session, site, us_num_to_node_id, existing=edges,
        ))

        return EditorState(
            site=site,
            rows=rows,
            nodes=nodes,
            edges=edges,
            pending_changes={"us_updates": [], "us_inserts": [], "us_deletes": []},
            group_by=group_by,
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
    def _build_edges_from_relationships_table(
        session: Session, site: str, us_num_to_node_id: dict, *, existing
    ) -> list[CytoscapeElement]:
        """Read stratigraphic relationships from ``us_relationships_table``.

        pyarchinit stores edges in a dedicated table (``us_from`` / ``us_to``
        / ``relationship_type``) — for sites like Ravenna with 1000+
        relationships, ``us_table.rapporti`` text is empty and everything
        lives here. We translate ``relationship_type`` through the same
        VocabProvider alias mapping used for ``rapporti`` tokens, and the
        same dedupe / inverse-pair rules apply.
        """
        try:
            from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry
            registry = EdgeRegistry()
        except Exception:
            return []

        SYMMETRIC = {"has_same_time"}
        INVERSE_PAIRS = {"overlies": "is_after", "is_after": "overlies"}

        # Seed seen-set with edges already produced from rapporti so we don't
        # duplicate the same relation across the two sources.
        seen: set[tuple] = set()
        for el in existing:
            ename = el.data.get("label")
            s = el.data.get("source")
            t = el.data.get("target")
            if not ename or not s or not t:
                continue
            if ename in SYMMETRIC:
                seen.add((ename, tuple(sorted((s, t)))))
            else:
                seen.add((ename, s, t))

        try:
            rows = session.execute(text(
                "SELECT us_from, us_to, relationship_type "
                "FROM us_relationships_table WHERE sito = :sito"
            ), {"sito": site}).fetchall()
        except Exception:
            return []

        out: list[CytoscapeElement] = []
        edge_counter = len(existing)

        for r in rows:
            us_from, us_to, rel_type = r[0], r[1], r[2]
            if not rel_type:
                continue
            try:
                u_from_int = int(us_from)
                u_to_int = int(us_to)
            except (ValueError, TypeError):
                continue
            source_id = us_num_to_node_id.get(u_from_int)
            target_id = us_num_to_node_id.get(u_to_int)
            if not source_id or not target_id:
                continue

            edge_name = registry.resolve_italian_alias(str(rel_type)) or rel_type

            if edge_name in SYMMETRIC:
                key = (edge_name, tuple(sorted((source_id, target_id))))
            else:
                key = (edge_name, source_id, target_id)
            if key in seen:
                continue
            inverse_name = INVERSE_PAIRS.get(edge_name)
            if inverse_name is not None:
                inverse_key = (inverse_name, target_id, source_id)
                if inverse_key in seen:
                    continue
            seen.add(key)

            edge_counter += 1
            out.append(CytoscapeElement(data={
                "id": f"e{edge_counter}",
                "source": source_id,
                "target": target_id,
                "label": edge_name,
            }))
        return out

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
