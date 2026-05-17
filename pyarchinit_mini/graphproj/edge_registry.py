"""Edge typing registry — wraps VocabProvider for canonical lookups."""
from typing import Optional

from pyarchinit_mini.vocab.provider import VocabProvider


class EdgeRegistry:
    """Resolves Italian rapporti aliases → canonical s3dgraphy edge type names.

    All data comes from VocabProvider (vocab_it.json edge_type_aliases).
    """

    def __init__(self) -> None:
        provider = VocabProvider.instance()
        self._alias_to_name: dict[str, str] = {}
        for edge in provider.get_edge_types():
            for alias in edge.italian_aliases:
                self._alias_to_name[alias.lower()] = edge.name
        self._sorted_aliases = sorted(self._alias_to_name.keys(), key=len, reverse=True)

    def resolve_italian_alias(self, text: str) -> Optional[str]:
        """Resolve an Italian alias string to canonical edge name.

        Exact match (lowercase): returns canonical edge name or None.
        """
        return self._alias_to_name.get(text.lower())

    def parse_rapporti_token(self, rel: str) -> tuple[Optional[str], Optional[str]]:
        """Parse one 'rapporti' token like 'coperto da 24' into (edge_name, target_us).

        Returns (None, None) if no alias matches.
        Tries longest aliases first to avoid prefix collisions.
        """
        rel_lower = rel.lower().strip()
        for alias in self._sorted_aliases:
            if rel_lower.startswith(alias):
                edge_name = self._alias_to_name[alias]
                tail = rel_lower[len(alias):].strip()
                target_us = "".join(c for c in tail if c.isdigit())
                if not target_us:
                    return edge_name, None
                return edge_name, target_us
        return None, None
