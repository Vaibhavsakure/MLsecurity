"""
PDF report generation and download endpoints.
Includes TTL-based cache eviction to prevent memory leaks.
"""
import io
import uuid
import datetime
import zipfile
import threading

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fpdf import FPDF
from typing import List

from schemas import ReportRequest

router = APIRouter(prefix="/api", tags=["reports"])

# ---------------------------------------------------------------------------
# In-memory report cache with TTL (10-minute expiry)
# ---------------------------------------------------------------------------
REPORT_CACHE_TTL_SECONDS = 600  # 10 minutes
_report_cache = {}
_cache_lock = threading.Lock()


def _cleanup_expired_reports():
    """Remove reports older than TTL from cache."""
    now = datetime.datetime.now()
    with _cache_lock:
        expired_keys = [
            k for k, v in _report_cache.items()
            if (now - v["created"]).total_seconds() > REPORT_CACHE_TTL_SECONDS
        ]
        for key in expired_keys:
            del _report_cache[key]


# ---------------------------------------------------------------------------
# PDF Generator
# ---------------------------------------------------------------------------
class SocialGuardPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(0, 180, 220)
        self.cell(0, 12, "SocialGuard AI", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "AI-Powered Fake Account Detection Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(6)
        self.set_draw_color(0, 180, 220)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"SocialGuard AI Report - Page {self.page_no()}", align="C")


def _generate_pdf_bytes(req: ReportRequest) -> bytes:
    """Generate PDF bytes for a single report."""
    pdf = SocialGuardPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    ts = req.timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 6, f"Generated: {ts}", new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, f"{req.platform.title()} Account Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    risk_colors = {"low": (34, 197, 94), "medium": (245, 158, 11), "high": (239, 68, 68)}
    rc = risk_colors.get(req.risk_level, (100, 100, 100))

    pdf.set_fill_color(rc[0], rc[1], rc[2])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(90, 12, f"  {req.label}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, f"Probability: {round(req.probability * 100, 1)}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 6, req.message)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "Input Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    alt = False
    for key, val in req.input_data.items():
        if alt:
            pdf.set_fill_color(240, 245, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        label = key.replace("_", " ").title()
        pdf.set_text_color(80, 80, 80)
        pdf.cell(90, 7, f"  {label}", fill=True)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, f"  {val}", fill=True, new_x="LMARGIN", new_y="NEXT")
        alt = not alt
    pdf.ln(6)

    if req.feature_importances:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 8, "Key Contributing Factors (SHAP Analysis)", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        max_val = max(abs(f["value"]) for f in req.feature_importances) if req.feature_importances else 1
        for feat in req.feature_importances:
            bar_width = min(abs(feat["value"]) / (max_val + 0.001) * 80, 80)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(60, 7, f"  {feat['feature']}")
            if feat["value"] > 0:
                pdf.set_fill_color(239, 68, 68)
                direction = "Increases Risk"
            else:
                pdf.set_fill_color(34, 197, 94)
                direction = "Decreases Risk"
            pdf.cell(bar_width, 7, "", fill=True)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 7, f"  {direction} ({feat['value']:+.4f})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 4, "Disclaimer: This report is generated by an AI model and should be used as a reference only. "
                         "The predictions are based on statistical patterns and may not be 100% accurate. "
                         "Always verify findings through additional investigation.")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/report/generate")
def generate_report(req: ReportRequest):
    _cleanup_expired_reports()
    pdf_bytes = _generate_pdf_bytes(req)
    filename = f"SocialGuard_{req.platform.title()}_Report.pdf"

    token = str(uuid.uuid4())
    with _cache_lock:
        _report_cache[token] = {
            "data": pdf_bytes,
            "filename": filename,
            "created": datetime.datetime.now()
        }

    return {"token": token, "filename": filename}


@router.get("/report/download/{token}")
def download_report(token: str):
    """Serve a previously generated PDF report by its token."""
    _cleanup_expired_reports()
    with _cache_lock:
        report = _report_cache.pop(token, None)
    if not report:
        raise HTTPException(status_code=404, detail="Report expired or not found")

    buf = io.BytesIO(report["data"])
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report["filename"]}"'}
    )


@router.post("/report/batch")
def batch_report(reports: List[ReportRequest]):
    """Generate a ZIP of PDF reports for batch analysis."""
    _cleanup_expired_reports()
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, req in enumerate(reports):
            pdf_bytes = _generate_pdf_bytes(req)
            filename = f"SocialGuard_{req.platform.title()}_Report_{i+1}.pdf"
            zf.writestr(filename, pdf_bytes)

    zip_buffer.seek(0)

    token = str(uuid.uuid4())
    with _cache_lock:
        _report_cache[token] = {
            "data": zip_buffer.getvalue(),
            "filename": "SocialGuard_Batch_Reports.zip",
            "created": datetime.datetime.now(),
            "media_type": "application/zip"
        }

    return {"token": token, "filename": "SocialGuard_Batch_Reports.zip"}


@router.get("/report/download-zip/{token}")
def download_zip_report(token: str):
    """Serve a batch ZIP report."""
    _cleanup_expired_reports()
    with _cache_lock:
        report = _report_cache.pop(token, None)
    if not report:
        raise HTTPException(status_code=404, detail="Report expired or not found")

    buf = io.BytesIO(report["data"])
    media_type = report.get("media_type", "application/pdf")
    return StreamingResponse(
        buf,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{report["filename"]}"'}
    )
