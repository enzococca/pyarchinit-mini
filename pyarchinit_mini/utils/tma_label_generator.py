"""
TMA Label Generator — produces printable PDF labels with QR codes.
Adapted from PyArchInit's pyarchinit_tma_label_pdf for use in pyarchinit-mini.
"""

import os
import tempfile
import logging
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


# Standard label sheet formats (mm)
LABEL_FORMATS = {
    'avery_l7160': {'width': 63.5, 'height': 38.1, 'per_row': 3, 'per_col': 7, 'margin': 2.5},
    'avery_l7163': {'width': 99.1, 'height': 38.1, 'per_row': 2, 'per_col': 7, 'margin': 2.5},
    'small_70x37': {'width': 70, 'height': 37, 'per_row': 3, 'per_col': 8, 'margin': 2},
    'medium_105x57': {'width': 105, 'height': 57, 'per_row': 2, 'per_col': 5, 'margin': 3},
    'single_a4': {'width': 210, 'height': 297, 'per_row': 1, 'per_col': 1, 'margin': 10},
}


class TMALabelGenerator:
    """Generate printable PDF labels for TMA records, with QR codes."""

    def __init__(self, label_format: str = 'avery_l7160'):
        self.label_format = LABEL_FORMATS.get(label_format, LABEL_FORMATS['avery_l7160'])
        self.page_size = A4
        self.page_width = A4[0] / mm
        self.page_height = A4[1] / mm

    def _calculate_positions(self):
        lw = self.label_format['width']
        lh = self.label_format['height']
        per_row = self.label_format['per_row']
        per_col = self.label_format['per_col']
        left = (self.page_width - per_row * lw) / 2
        top = (self.page_height - per_col * lh) / 2
        positions = []
        for col in range(per_col):
            for row in range(per_row):
                x = left + row * lw
                y = self.page_height - top - (col + 1) * lh
                positions.append((x * mm, y * mm))
        return positions

    def _generate_qr(self, data: str) -> Optional[str]:
        if not HAS_QRCODE:
            return None
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=5,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png', mode='wb')
            tmp.close()
            img.save(tmp.name, format='PNG')
            return tmp.name if os.path.exists(tmp.name) else None
        except Exception as e:
            logger.warning(f"QR generation failed: {e}")
            return None

    def _format_qr_data(self, tma: Dict[str, Any]) -> str:
        """Build human-readable QR text (also readable by smartphone camera)."""
        parts = ['SCHEDA TMA']
        if tma.get('cassetta'):
            parts.append(f"Cassetta: {tma['cassetta']}")
        if tma.get('sito'):
            parts.append(f"Sito: {tma['sito']}")
        if tma.get('localita'):
            parts.append(f"Localita: {tma['localita']}")
        if tma.get('area'):
            parts.append(f"Area: {tma['area']}")
        if tma.get('settore'):
            parts.append(f"Settore: {tma['settore']}")
        if tma.get('dscu'):
            parts.append(f"US: {tma['dscu']}")
        if tma.get('inventario'):
            parts.append(f"Inventario: {tma['inventario']}")
        if tma.get('saggio'):
            parts.append(f"Saggio: {tma['saggio']}")
        if tma.get('vano_locus'):
            parts.append(f"Vano/Locus: {tma['vano_locus']}")
        if tma.get('ogtm'):
            parts.append(f"Materiale: {tma['ogtm']}")
        if tma.get('dtzg'):
            parts.append(f"Cronologia: {tma['dtzg']}")
        if tma.get('id'):
            parts.append(f"ID: {tma['id']}")
        return "\n".join(parts)

    def _draw_label(self, c, x, y, tma: Dict[str, Any]):
        lw = self.label_format['width'] * mm
        lh = self.label_format['height'] * mm
        margin = self.label_format['margin'] * mm

        # Border
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.rect(x, y, lw, lh)

        # QR code on the left
        qr_size = min(lh - 2 * margin, lw * 0.35)
        qr_file = self._generate_qr(self._format_qr_data(tma))
        if qr_file:
            try:
                c.drawImage(qr_file, x + margin, y + (lh - qr_size) / 2,
                            width=qr_size, height=qr_size)
                try:
                    os.unlink(qr_file)
                except OSError:
                    pass
            except Exception as e:
                logger.warning(f"draw QR failed: {e}")

        # Text on the right
        text_x = x + qr_size + margin * 2
        text_w = lw - qr_size - margin * 3
        text_top = y + lh - margin

        c.setFillColor(colors.black)
        line_h = 3.2 * mm

        def line(text, font='Helvetica', size=7, bold=False):
            nonlocal text_top
            if text_top < y + margin:
                return
            c.setFont('Helvetica-Bold' if bold else font, size)
            text_top -= line_h
            # Truncate to fit width
            max_chars = max(int(text_w / (size * 0.55)), 12)
            txt = str(text)[:max_chars]
            c.drawString(text_x, text_top, txt)

        line(f"Cassetta: {tma.get('cassetta', '-')}", size=8, bold=True)
        if tma.get('sito'):
            line(f"Sito: {tma['sito']}", size=6)
        if tma.get('area'):
            line(f"Area: {tma['area']}  US: {tma.get('dscu', '-')}", size=6)
        if tma.get('inventario'):
            line(f"Inv: {tma['inventario']}", size=6)
        if tma.get('ogtm'):
            line(f"Mat: {tma['ogtm']}", size=6)
        if tma.get('dtzg'):
            line(f"Cronol: {tma['dtzg']}", size=6)

    def generate(self, tma_records: List[Dict[str, Any]], output_path: str) -> str:
        """Generate a PDF with labels for the given TMA records."""
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        positions = self._calculate_positions()
        labels_per_page = len(positions)

        for i, tma in enumerate(tma_records):
            if i > 0 and i % labels_per_page == 0:
                c.showPage()
            x, y = positions[i % labels_per_page]
            self._draw_label(c, x, y, tma)

        c.save()
        return output_path
