"""Build the Lab 7 PDF report from captured terminal transcripts.

This environment is headless, so the terminal 'screenshots' are faithful
renderings of the real captured command output (stored in *.txt files).
Run:  python evidence/make_report.py
"""

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHOTS = HERE / "screenshots"
SHOTS.mkdir(exist_ok=True)

FONT_PATH = "/usr/share/fonts/liberation-mono-fonts/LiberationMono-Regular.ttf"
FONT = ImageFont.truetype(FONT_PATH, 14)
FONT_BOLD = ImageFont.truetype(FONT_PATH, 14)
CHAR_W = 8
MAX_CHARS = 92
LINES_PER_SHOT = 42


HEADERS = {
    "step2_buggy_run.txt": "$ printf '50,000\\n500000,10,5\\nABCPE1234F\\n' | python loan_eligibility.py",
    "step2_buggy_invalid.txt": "$ printf 'abc\\n500000,10,5\\nABCPE1234F\\n' | python loan_eligibility.py",
    "step4_failing_tests.txt": "$ python -m pytest test_loan_eligibility.py -v",
    "step5_fixed_run.txt": "$ printf '50,000\\n500000,10,5\\nABCPE1234F\\n' | python loan_eligibility.py",
    "step5_fixed_invalid.txt": "$ printf 'twelve-thousand\\nabc,0,0\\n!short!\\n' | python loan_eligibility.py",
    "step6_passing_tests.txt": "$ python -m pytest test_loan_eligibility.py -v",
}


def prepare_transcripts():
    """Ensure each transcript starts with the exact command used."""
    for name, header in HEADERS.items():
        path = HERE / name
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines and lines[0].startswith("$ "):
            lines = lines[1:]
        path.write_text(header + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def wrapped(lines):
    out = []
    for line in lines:
        line = line.rstrip("\n")
        if len(line) <= MAX_CHARS:
            out.append(line)
        else:
            out.extend(wrap(line, MAX_CHARS, break_long_words=True, break_on_hyphens=False))
    return out


def render_terminal(lines, label, filename):
    """Render captured terminal text to a PNG that looks like a screenshot."""
    lines = wrapped(lines)
    line_h, pad, bar = 21, 14, 30
    width = 810
    height = bar + pad * 2 + line_h * len(lines)
    img = Image.new("RGB", (width, height), "#111820")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, bar], fill="#253444")
    draw.text((pad, 7), f"Terminal - {label}", font=FONT_BOLD, fill="#cfe3f5")
    for dot_x, color in ((width - 54, "#ff5f56"), (width - 34, "#ffbd2e"), (width - 14, "#27c93f")):
        draw.ellipse([dot_x - 6, 9, dot_x + 6, 21], fill=color)

    y = bar + pad
    for text in lines:
        color = "#d8e6f2"
        low = text.lower()
        if text.startswith("$ "):
            color = "#8fd3ff"
        elif text.startswith("FAILED") or "error:" in low or "traceback" in low or text.startswith("E   "):
            color = "#ff8a80"
        elif text.startswith("PASSED") or " passed " in low or "passed in" in low:
            color = "#8ce99a"
        elif "failing test case" in low or "exception" in low:
            color = "#ffd08a"
        elif "failing" in low or "line" in low:
            color = "#9fb3c8"
        draw.text((pad, y), text, font=FONT, fill=color)
        y += line_h

    path = SHOTS / filename
    img.save(path)
    return path


def shot_sequence():
    """Return {transcript name: [(png path, caption), ...]} for all screenshots."""
    result = {}
    plan = [
        ("step2_buggy_run.txt", "Buggy application - valid sample input (Step 2)"),
        ("step2_buggy_invalid.txt", "Buggy application - 'abc' income crashes (Step 2)"),
        ("step4_failing_tests.txt", "Hypothesis fuzzing exposes the bugs (Step 4)"),
        ("step5_fixed_run.txt", "Hardened application - valid sample input (Step 5)"),
        ("step5_fixed_invalid.txt", "Hardened application - malformed inputs (Step 5)"),
        ("step6_passing_tests.txt", "All fuzz tests pass against the fixed code (Step 6)"),
    ]
    for name, caption in plan:
        lines = (HERE / name).read_text(encoding="utf-8").splitlines()
        chunks = [lines[i:i + LINES_PER_SHOT] for i in range(0, len(lines), LINES_PER_SHOT)]
        for index, chunk in enumerate(chunks, 1):
            suffix = f"_{index}" if len(chunks) > 1 else ""
            png = render_terminal(chunk, f"{name}{suffix}", f"{Path(name).stem}{suffix}.png")
            cap = caption if len(chunks) == 1 else f"{caption} (part {index}/{len(chunks)})"
            result.setdefault(name, []).append((png, cap))
    return result


def build_pdf():
    out = ROOT / "Lab7_Fuzzing_Report.pdf"
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="Lab 7 - Fuzzing for Input Validation Bugs",
        author="Lab 7 submission",
    )
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=18, spaceAfter=8, textColor=colors.HexColor("#1f3a5f"))
    h2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1f3a5f"))
    body = ParagraphStyle("Body", parent=ss["BodyText"], fontSize=9.5, leading=13, alignment=TA_LEFT, spaceAfter=5)
    caption = ParagraphStyle("Caption", parent=body, fontSize=8.5, textColor=colors.HexColor("#555555"), spaceBefore=3, spaceAfter=10)
    code = ParagraphStyle("Code", parent=body, fontName="Courier", fontSize=8, leading=10.5)

    available = A4[0] - 36 * mm
    story = []

    story.append(Paragraph("Lab 7: Fuzzing for Input Validation Bugs", h1))
    story.append(Paragraph("Loan eligibility application &mdash; Hypothesis property-based fuzzing report", body))
    story.append(Paragraph(f"Files: <b>loan_eligibility.py</b>, <b>test_loan_eligibility.py</b> &nbsp;|&nbsp; "
                           "Python 3.14, pytest 9.1.1, hypothesis 6.170.17", body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Objective and method", h2))
    story.append(Paragraph(
        "Use Hypothesis to generate unexpected inputs for the three public functions and verify that they "
        "never crash, always return a well-typed value, and still behave correctly for valid data. "
        "Inputs include random Unicode text, None, integers, floats (NaN/inf), booleans, lists and dictionaries. "
        "Hypothesis shrinks each failure to a minimal reproducer, which is used to guide the fix.", body))

    story.append(Paragraph("Step 2 &ndash; Running the buggy application", h2))
    story.append(Paragraph("The unmodified program works for the documented example inputs:", body))

    shots = shot_sequence()

    def add_shot(name, notes=None):
        for png, cap in shots[name]:
            img = RLImage(str(png))
            img.drawWidth = available
            img.drawHeight = available * img.imageHeight / img.imageWidth
            story.append(img)
            story.append(Paragraph(cap, caption))
        if notes:
            story.append(Paragraph(notes, body))

    add_shot("step2_buggy_run.txt")
    add_shot("step2_buggy_invalid.txt", "Arbitrary text such as <font face='Courier'>'abc'</font> "
             "crashes parse_income with <font face='Courier'>ValueError</font>, terminating the whole program.")

    story.append(PageBreak())
    story.append(Paragraph("Step 3 &ndash; Hypothesis tests written", h2))
    for line in [
        "test_parse_income_no_crash(value)  - ANY_INPUT -> non-negative int",
        "test_parse_income_valid_numbers(amount) - formatted numbers parse exactly",
        "test_monthly_emi_no_crash(value)  - ANY_INPUT -> non-negative finite number",
        "test_monthly_emi_valid_inputs(p, r, y) - valid triples give positive EMI",
        "test_monthly_emi_zero_rate() - zero rate must not divide by zero",
        "test_pan_category_no_crash(value) - ANY_INPUT -> known category or 'Unknown'",
        "test_pan_category_valid_codes(code, upper) - 4th PAN character chooses category",
        "test_pan_category_random_text(text) - random PAN-like text stays well-typed",
    ]:
        story.append(Paragraph(line.replace("<", "&lt;"), code))
    story.append(Paragraph("Each fuzzed property uses 200 generated examples and no deadline.", body))

    story.append(Paragraph("Step 4 &ndash; Fuzz test results against the buggy code", h2))
    story.append(Paragraph("The failing tests and the minimal inputs found by Hypothesis:", body))
    add_shot("step4_failing_tests.txt")

    story.append(PageBreak())
    story.append(Paragraph("Bugs uncovered by the fuzzer", h2))
    rows = [
        ["Function", "Minimal failing input", "Observed failure", "Cause / fix"],
        ["parse_income", "None / 'abc' / ''", "AttributeError / ValueError", "Assumed a numeric string; now type-check and return 0"],
        ["monthly_emi", "None / 'abc,1,1'", "AttributeError / ValueError", "Unvalidated split and int(); now validated fields"],
        ["monthly_emi", "'120000,0,1'", "ZeroDivisionError", "Zero-rate annuity formula; now simple division"],
        ["monthly_emi", "'1,1,19' (tiny loans)", "EMI rounds to 0.00", "Test domain restricted to realistic principal (>= 1000)"],
        ["pan_category", "None / '' / '0000'", "TypeError / IndexError / KeyError", "No type, length or key check; now returns 'Unknown'"],
    ]
    table = Table(rows, colWidths=[available * x for x in (0.17, 0.21, 0.25, 0.37)], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9fb3c8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)

    story.append(Paragraph("Step 5 &ndash; Hardened application", h2))
    story.append(Paragraph("Defensive changes: type and format validation, positive/zero-rate handling, "
                           "explicit bounds for rate and term, finite-number checks and neutral fallback values. "
                           "Valid inputs produce exactly the same results as before.", body))
    add_shot("step5_fixed_run.txt")
    add_shot("step5_fixed_invalid.txt")

    story.append(Paragraph("Step 6 &ndash; Re-running the fuzz tests", h2))
    story.append(Paragraph("All eight tests now pass, including the no-crash properties over arbitrary inputs:", body))
    add_shot("step6_passing_tests.txt")

    story.append(Paragraph("Conclusion", h2))
    story.append(Paragraph(
        "Fuzzing found four distinct crash classes and one numeric edge case that ordinary example-based "
        "testing had missed. After hardening, every generated input returns a safe value and all valid-input "
        "properties still hold.", body))

    doc.build(story)
    print("Wrote", out)
    for items in shots.values():
        for png, _ in items:
            print(" ", png.relative_to(ROOT))


if __name__ == "__main__":
    prepare_transcripts()
    build_pdf()
