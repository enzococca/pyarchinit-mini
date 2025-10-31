"""
Period Filter

Utility per filtrare proxies basati su cronologia e periodizzazione.
Integra datazioni BCE/CE con filtri temporali per visualizzazione 3D.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class PeriodFilter:
    """
    Filtro per periodi cronologici

    Permette di filtrare proxies basati su:
    - Periodo archeologico (Bronze Age, Iron Age, etc.)
    - Range cronologico (BCE/CE)
    - Fase/sottofase
    - Affidabilità datazione
    """

    def __init__(self):
        """Initialize period filter"""
        pass

    def filter_by_period(
        self, proxies: List[Dict[str, Any]], period_names: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter proxies by period name

        Args:
            proxies: List of proxy metadata dicts
            period_names: List of period names to include

        Returns:
            Filtered list of proxies
        """
        if not period_names:
            return proxies

        filtered = []
        for proxy in proxies:
            period = proxy.get("chronology", {}).get("period_name", "")
            if period in period_names:
                filtered.append(proxy)

        logger.info(
            f"Filtered {len(filtered)}/{len(proxies)} proxies by period {period_names}"
        )
        return filtered

    def filter_by_date_range(
        self,
        proxies: List[Dict[str, Any]],
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter proxies by chronological range

        Args:
            proxies: List of proxy metadata dicts
            start_date: Start date (negative = BCE, positive = CE)
            end_date: End date (negative = BCE, positive = CE)

        Returns:
            Filtered list of proxies

        Example:
            filter_by_date_range(proxies, -1200, -800)  # 1200-800 BCE
            filter_by_date_range(proxies, -500, 500)    # 500 BCE - 500 CE
        """
        if start_date is None and end_date is None:
            return proxies

        filtered = []
        for proxy in proxies:
            chronology = proxy.get("chronology", {})
            dating_start = chronology.get("dating_start")
            dating_end = chronology.get("dating_end")

            if dating_start is None or dating_end is None:
                # No dating info - skip or include based on policy
                continue

            # Check if proxy dating overlaps with filter range
            overlaps = self._ranges_overlap(
                dating_start, dating_end, start_date, end_date
            )

            if overlaps:
                filtered.append(proxy)

        logger.info(
            f"Filtered {len(filtered)}/{len(proxies)} proxies "
            f"by date range {start_date} to {end_date}"
        )
        return filtered

    def filter_by_timeline_position(
        self, proxies: List[Dict[str, Any]], min_pos: float, max_pos: float
    ) -> List[Dict[str, Any]]:
        """
        Filter by timeline slider position (0.0-1.0)

        Useful for UI timeline controls where user drags a range slider.

        Args:
            proxies: List of proxy metadata dicts
            min_pos: Minimum position (0.0 = oldest)
            max_pos: Maximum position (1.0 = newest)

        Returns:
            Filtered list of proxies
        """
        if not proxies:
            return []

        # Get overall date range
        all_dates = []
        for proxy in proxies:
            chronology = proxy.get("chronology", {})
            if chronology.get("dating_start") and chronology.get("dating_end"):
                all_dates.append(chronology["dating_start"])
                all_dates.append(chronology["dating_end"])

        if not all_dates:
            return proxies

        min_date = min(all_dates)
        max_date = max(all_dates)
        date_range = max_date - min_date

        # Calculate date range from slider positions
        filter_start = min_date + (date_range * min_pos)
        filter_end = min_date + (date_range * max_pos)

        return self.filter_by_date_range(proxies, int(filter_start), int(filter_end))

    def filter_by_reliability(
        self, proxies: List[Dict[str, Any]], min_reliability: str = "Bassa"
    ) -> List[Dict[str, Any]]:
        """
        Filter by dating reliability

        Args:
            proxies: List of proxy metadata dicts
            min_reliability: Minimum reliability ("Alta", "Media", "Bassa")

        Returns:
            Filtered list of proxies
        """
        reliability_order = {"Alta": 3, "Media": 2, "Bassa": 1}
        min_level = reliability_order.get(min_reliability, 1)

        filtered = []
        for proxy in proxies:
            affidabilita = proxy.get("chronology", {}).get("affidabilita", "Bassa")
            level = reliability_order.get(affidabilita, 1)

            if level >= min_level:
                filtered.append(proxy)

        logger.info(
            f"Filtered {len(filtered)}/{len(proxies)} proxies "
            f"by reliability >= {min_reliability}"
        )
        return filtered

    def get_period_statistics(
        self, proxies: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics by period

        Returns:
            Dict mapping period name to statistics
        """
        stats = {}

        for proxy in proxies:
            period = proxy.get("chronology", {}).get("period_name", "Unknown")

            if period not in stats:
                stats[period] = {
                    "count": 0,
                    "us_ids": [],
                    "date_range": {"start": None, "end": None},
                }

            stats[period]["count"] += 1
            stats[period]["us_ids"].append(proxy["us_id"])

            # Update date range
            dating_start = proxy.get("chronology", {}).get("dating_start")
            dating_end = proxy.get("chronology", {}).get("dating_end")

            if dating_start:
                if stats[period]["date_range"]["start"] is None:
                    stats[period]["date_range"]["start"] = dating_start
                else:
                    stats[period]["date_range"]["start"] = min(
                        stats[period]["date_range"]["start"], dating_start
                    )

            if dating_end:
                if stats[period]["date_range"]["end"] is None:
                    stats[period]["date_range"]["end"] = dating_end
                else:
                    stats[period]["date_range"]["end"] = max(
                        stats[period]["date_range"]["end"], dating_end
                    )

        return stats

    def get_timeline_data(
        self, proxies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get data for timeline visualization

        Returns:
            Dict with timeline data for UI
        """
        if not proxies:
            return {
                "min_date": 0,
                "max_date": 0,
                "total_range": 0,
                "periods": {},
                "us_timeline": [],
            }

        # Collect all dates
        all_dates = []
        us_timeline = []

        for proxy in proxies:
            chronology = proxy.get("chronology", {})
            dating_start = chronology.get("dating_start")
            dating_end = chronology.get("dating_end")

            if dating_start and dating_end:
                all_dates.extend([dating_start, dating_end])

                us_timeline.append({
                    "us_id": proxy["us_id"],
                    "period": chronology.get("period_name", "Unknown"),
                    "start": dating_start,
                    "end": dating_end,
                    "label": f"US {proxy['us_id']}",
                })

        if not all_dates:
            return {
                "min_date": 0,
                "max_date": 0,
                "total_range": 0,
                "periods": {},
                "us_timeline": [],
            }

        min_date = min(all_dates)
        max_date = max(all_dates)

        # Get period statistics
        period_stats = self.get_period_statistics(proxies)

        return {
            "min_date": min_date,
            "max_date": max_date,
            "total_range": max_date - min_date,
            "periods": period_stats,
            "us_timeline": sorted(us_timeline, key=lambda x: x["start"]),
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _ranges_overlap(
        self,
        a_start: int,
        a_end: int,
        b_start: Optional[int],
        b_end: Optional[int],
    ) -> bool:
        """Check if two date ranges overlap"""
        if b_start is None and b_end is None:
            return True  # No filter specified

        if b_start is None:
            # Only end date specified
            return a_start <= b_end

        if b_end is None:
            # Only start date specified
            return a_end >= b_start

        # Both specified - check overlap
        return not (a_end < b_start or a_start > b_end)

    def format_date(self, date: int) -> str:
        """
        Format date for display

        Args:
            date: Date as integer (negative = BCE, positive = CE)

        Returns:
            Formatted string (e.g., "1200 BCE", "500 CE")
        """
        if date < 0:
            return f"{abs(date)} BCE"
        elif date > 0:
            return f"{date} CE"
        else:
            return "0"


# ============================================================================
# Helper Functions
# ============================================================================


def filter_proxies_by_period(
    proxies: List[Dict[str, Any]], period_names: List[str]
) -> List[Dict[str, Any]]:
    """
    Quick helper to filter by period names

    Args:
        proxies: List of proxies
        period_names: List of period names

    Returns:
        Filtered proxies
    """
    filter_obj = PeriodFilter()
    return filter_obj.filter_by_period(proxies, period_names)


def filter_proxies_by_dates(
    proxies: List[Dict[str, Any]], start: int, end: int
) -> List[Dict[str, Any]]:
    """
    Quick helper to filter by date range

    Args:
        proxies: List of proxies
        start: Start date (negative = BCE)
        end: End date (negative = BCE)

    Returns:
        Filtered proxies
    """
    filter_obj = PeriodFilter()
    return filter_obj.filter_by_date_range(proxies, start, end)
