"""
QuickHire PDF Resume Export Engine
Supports 5 templates, photo embedding, smart page compression, and page-break prevention.
"""
import io, re
from pathlib import Path
from dataclasses import dataclass, field
from fpdf import FPDF

# ── Font discovery ──────────────────────────────────────────
FONT_PATH = None
FONT_BOLD_PATH = None
for candidate in [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/STSONG.TTF",
]:
    if Path(candidate).exists():
        if not FONT_PATH:
            FONT_PATH = candidate
        elif not FONT_BOLD_PATH and ("bd" in candidate.lower() or "hei" in candidate.lower()):
            FONT_BOLD_PATH = candidate

if not FONT_BOLD_PATH:
    FONT_BOLD_PATH = FONT_PATH  # fallback

HAS_CJK = FONT_PATH is not None

# ── Constants ───────────────────────────────────────────────
PAGE_W, PAGE_H = 210, 297  # A4 in mm
DEFAULT_MARGIN = 20
MIN_MARGIN = 12
DEFAULT_FONT_SIZE = 10
MIN_FONT_SIZE = 8.5
DEFAULT_LINE_H = 5.5
MIN_LINE_H = 4.5
CONTENT_PRIORITY_HIGH = {"work", "projects", "skills"}
CONTENT_PRIORITY_MEDIUM = {"education", "certificates", "languages"}
CONTENT_PRIORITY_LOW = {"self_eval", "summary"}

REDUNDANT_PREFIXES = [
    r"^负责\s*", r"^参与\s*", r"^协助\s*", r"^帮助\s*",
    r"^主要\s*", r"^积极\s*", r"^主动\s*", r"^持续\s*",
]


# ── Data structures ─────────────────────────────────────────
@dataclass
class ResumeSection:
    title: str
    key: str
    lines: list = field(default_factory=list)
    priority: str = "medium"


@dataclass
class ParsedResume:
    name: str = ""
    contact: dict = field(default_factory=dict)  # {email, phone, ...}
    sections: list = field(default_factory=list)  # list[ResumeSection]
    raw_lines: list = field(default_factory=list)


# ── Content parser ──────────────────────────────────────────
SECTION_PATTERNS = [
    (r"教育(?:经历|背景)?[：:]", "education", "medium"),
    (r"工作(?:经历|经验)?[：:]", "work", "high"),
    (r"项目(?:经历|经验)?[：:]", "projects", "high"),
    (r"(?:专业)?技能[：:]?", "skills", "high"),
    (r"(?:自我)?评价[：:]", "self_eval", "low"),
    (r"证书[：:]", "certificates", "medium"),
    (r"语言(?:能力)?[：:]", "languages", "medium"),
    (r"实习(?:经历)?[：:]", "internships", "medium"),
]


def parse_resume(content: str) -> ParsedResume:
    """Parse raw resume text into structured sections."""
    result = ParsedResume()
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    result.raw_lines = lines

    # Extract name from first line (e.g. "张三 | 男 | 1997年 | 3年")
    first = lines[0]
    name_match = re.match(r"^([^\s|｜]+)", first)
    if name_match:
        result.name = re.sub(r"[：:，,。●◆]+$", "", name_match.group(1)).strip()

    # Extract contact info from first few lines
    for line in lines[:5]:
        email_m = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", line)
        if email_m:
            result.contact["email"] = email_m.group(1)
        phone_m = re.search(r"(1[3-9]\d{9})", line)
        if phone_m:
            result.contact["phone"] = phone_m.group(1)
        if "期望" in line or "意向" in line:
            result.contact["target"] = re.sub(r"期望(?:职位|岗位)?[：:]?\s*", "", line).strip()

    # Split into sections
    current_section = None
    section_lines = []

    for line in lines:
        matched = False
        for pattern, key, priority in SECTION_PATTERNS:
            if re.match(pattern, line):
                if current_section and section_lines:
                    result.sections.append(ResumeSection(
                        title=current_section[0], key=current_section[1],
                        lines=list(section_lines), priority=current_section[2],
                    ))
                title = re.sub(r"[：:]$", "", re.match(pattern, line).group()).strip()
                current_section = (title, key, priority)
                section_lines = []
                # Check if there's content after the match on the same line
                remaining = re.sub(pattern, "", line).strip()
                if remaining:
                    section_lines.append(remaining)
                matched = True
                break

        if not matched:
            if current_section:
                section_lines.append(line)

    if current_section and section_lines:
        result.sections.append(ResumeSection(
            title=current_section[0], key=current_section[1],
            lines=list(section_lines), priority=current_section[2],
        ))

    return result


# ── Compression engine ──────────────────────────────────────
class CompressionEngine:
    """Applies layered compression to fit content to target page count."""

    def __init__(self):
        self.font_size = DEFAULT_FONT_SIZE
        self.line_h = DEFAULT_LINE_H
        self.margin = DEFAULT_MARGIN

    def apply_layer1(self, parsed: ParsedResume, target_pages: int) -> bool:
        """Layout compression: reduce font, spacing, margins."""
        steps = [
            (9.5, 5.2, 18),   # step 1
            (9.0, 5.0, 16),   # step 2
            (9.0, 4.8, 15),   # step 3
            (8.5, 4.5, 12),   # step 4 (minimum)
        ]
        for fs, lh, margin in steps:
            self.font_size = fs
            self.line_h = lh
            self.margin = margin
            pages = self._estimate_pages(parsed)
            if pages <= target_pages:
                return True
        return False

    def apply_layer2(self, parsed: ParsedResume) -> ParsedResume:
        """Content trimming: remove redundant prefixes, merge short lines, limit bullet count."""
        for section in parsed.sections:
            cleaned = []
            for line in section.lines:
                line = line.strip()
                # Remove redundant prefixes
                for prefix in REDUNDANT_PREFIXES:
                    line = re.sub(prefix, "", line)
                if line:
                    cleaned.append(line)

            # Merge consecutive short lines (< 20 chars) into one
            merged = []
            i = 0
            while i < len(cleaned):
                current = cleaned[i]
                # If this is a bullet point and next line is short non-bullet
                if current.startswith(("-", "·", "•")) and i + 1 < len(cleaned):
                    next_line = cleaned[i + 1]
                    if (not re.match(r"^[-·•\d]", next_line) and
                            len(next_line) < 30):
                        current = current.rstrip("。，,.") + "；" + next_line
                        i += 1
                merged.append(current)
                i += 1

            # Limit work/project bullets to 2-3 per entry
            if section.key in ("work", "projects"):
                limited = []
                bullet_count = 0
                for line in merged:
                    if re.match(r"^[-·•]", line):
                        bullet_count += 1
                        if bullet_count <= 3:
                            limited.append(line)
                    else:
                        bullet_count = 0
                        limited.append(line)
                merged = limited

            section.lines = merged
        return parsed

    def apply_layer3(self, parsed: ParsedResume, target_pages: int) -> ParsedResume:
        """Priority-based section removal / truncation."""
        # Try removing low-priority sections first
        for section in parsed.sections:
            if section.priority == "low":
                section.lines = []
                if self._estimate_pages(parsed) <= target_pages:
                    return parsed

        # Truncate medium-priority sections
        for section in parsed.sections:
            if section.priority == "medium" and len(section.lines) > 1:
                section.lines = section.lines[:1]
                if self._estimate_pages(parsed) <= target_pages:
                    return parsed

        return parsed

    def _estimate_pages(self, parsed: ParsedResume) -> int:
        """Rough page count estimation based on content volume."""
        total_chars = sum(len(l) for s in parsed.sections for l in s.lines)
        total_chars += sum(len(l) for l in parsed.raw_lines[:5])  # header
        chars_per_page = (PAGE_W - 2 * self.margin) * (PAGE_H - 2 * self.margin) / (self.font_size * 0.6)
        return max(1, round(total_chars / chars_per_page))

    def compress(self, parsed: ParsedResume, page_limit: int) -> tuple:
        """Apply layers until content fits within page_limit."""
        natural_pages = self._estimate_pages(parsed)
        if natural_pages <= page_limit:
            return parsed, self.font_size, self.line_h, self.margin

        # Layer 1: layout
        if self.apply_layer1(parsed, page_limit):
            return parsed, self.font_size, self.line_h, self.margin

        # Layer 2: content trim
        parsed = self.apply_layer2(parsed)
        pages = self._estimate_pages(parsed)
        if pages <= page_limit:
            return parsed, self.font_size, self.line_h, self.margin
        if self.apply_layer1(parsed, page_limit):
            return parsed, self.font_size, self.line_h, self.margin

        # Layer 3: priority removal
        parsed = self.apply_layer3(parsed, page_limit)
        return parsed, self.font_size, self.line_h, self.margin


# ── Base PDF class ──────────────────────────────────────────
class ResumePDF(FPDF):
    """Extended FPDF with CJK support and resume helpers."""

    def __init__(self, font_size=DEFAULT_FONT_SIZE, line_h=DEFAULT_LINE_H, margin=DEFAULT_MARGIN):
        super().__init__()
        self.fs = font_size
        self.lh = line_h
        self.margin = margin
        # Ensure fpdf internal margins match our custom margin
        self.l_margin = margin
        self.r_margin = margin
        self.t_margin = margin
        self._setup_fonts()

    def _setup_fonts(self):
        if HAS_CJK:
            self.add_font("cjk", "", FONT_PATH, uni=True)
            self.add_font("cjk", "B", FONT_BOLD_PATH, uni=True)
        self.family = "cjk" if HAS_CJK else "Helvetica"

    def set_fs(self, size=None):
        """Set font with current family and size."""
        self.set_font(self.family, "", size or self.fs)

    def set_fs_bold(self, size=None):
        size = size or self.fs
        if HAS_CJK:
            self.set_font(self.family, "B", size)
        else:
            self.set_font(self.family, "B", size)

    def write_line(self, text, size=None, bold=False, align="L", indent=0):
        """Write a single line with optional indent."""
        x = self.margin + indent
        self.set_x(x)
        if bold:
            self.set_fs_bold(size)
        else:
            self.set_fs(size)
        self.cell(self.w - 2 * self.margin - indent, self.lh + 1, text, align=align,
                   new_x="LMARGIN", new_y="NEXT")

    def write_section_title(self, title):
        """Section heading with underline accent."""
        self.ln(2)
        self.set_draw_color(5, 150, 105)
        self.set_line_width(0.4)
        y = self.get_y()
        self.write_line(title, size=self.fs + 1, bold=True)
        nx = self.margin + self.get_string_width(title) + 4
        self.line(nx, y + self.lh + 1.5, self.w - self.margin, y + self.lh + 1.5)
        self.ln(1)

    def write_bullet(self, text, indent=6):
        """Write a bullet-point line."""
        self.write_line(f"• {text}", indent=indent)

    def write_multiline(self, text, indent=0, max_width=None):
        """Write text that may wrap across lines."""
        width = max_width or (self.w - 2 * self.margin - indent)
        self.set_fs()
        x = self.margin + indent
        self.set_x(x)
        self.multi_cell(width, self.lh + 0.8, text, align="L")

    def embed_photo(self, photo_bytes, x, y, w, h):
        """Embed photo from bytes into the PDF."""
        try:
            from PIL import Image as PILImage
            img = PILImage.open(io.BytesIO(photo_bytes))
            buf = io.BytesIO()
            # Convert to RGB if RGBA
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            self.image(buf, x=x, y=y, w=w, h=h)
        except ImportError:
            # Fallback: try direct (works for JPEG)
            self.image(io.BytesIO(photo_bytes), x=x, y=y, w=w, h=h)

    def check_page_break(self, needed_height):
        """Check if we need a page break; return True if break occurred."""
        if self.get_y() + needed_height > PAGE_H - self.margin:
            self.add_page()
            return True
        return False


# ── Template 1: Classic Two-Column ─────────────────────────
def template_classic_two_column(pdf: ResumePDF, parsed: ParsedResume, photo_bytes=None):
    """Left sidebar with photo + name + contact; right content with green accents."""
    left_w = 52
    gap = 6
    right_x = pdf.margin + left_w + gap
    right_w = pdf.w - right_x - pdf.margin

    family = pdf.family

    # ── Left column: light green background ──
    pdf.set_fill_color(245, 250, 248)
    pdf.rect(pdf.margin, pdf.margin, left_w, PAGE_H - 2 * pdf.margin, "F")

    # Photo
    photo_size = min(left_w - 12, 38)
    photo_x = pdf.margin + (left_w - photo_size) / 2
    photo_y = pdf.margin + 6
    if photo_bytes:
        pdf.embed_photo(photo_bytes, photo_x, photo_y, photo_size, photo_size)

    cur_y = (photo_y + photo_size + 5) if photo_bytes else (pdf.margin + 10)

    # Name (green, bold)
    pdf.set_font(family, "B", pdf.fs + 3)
    pdf.set_text_color(5, 150, 105)
    pdf.set_xy(pdf.margin, cur_y)
    pdf.cell(left_w, pdf.lh + 3, parsed.name, align="C")
    cur_y = pdf.get_y() + 2

    # Contact info (black, small)
    pdf.set_font(family, "", pdf.fs - 1.5)
    pdf.set_text_color(60, 60, 60)
    for key, val in parsed.contact.items():
        if key == "target":
            continue
        pdf.set_xy(pdf.margin + 2, cur_y)
        pdf.cell(left_w - 4, pdf.lh + 1.5, val, align="C")
        cur_y = pdf.get_y()

    # Skills in sidebar
    skills_section = next((s for s in parsed.sections if s.key == "skills"), None)
    if skills_section:
        cur_y += 3
        pdf.set_font(family, "B", pdf.fs - 0.5)
        pdf.set_text_color(5, 150, 105)
        pdf.set_xy(pdf.margin, cur_y)
        pdf.cell(left_w, pdf.lh + 1.5, "专业技能", align="C")
        cur_y = pdf.get_y() + 1

        pdf.set_font(family, "", pdf.fs - 1.5)
        pdf.set_text_color(60, 60, 60)
        skill_text = " · ".join(skills_section.lines[:6])
        pdf.set_xy(pdf.margin + 2, cur_y)
        pdf.multi_cell(left_w - 4, pdf.lh + 1.5, skill_text, align="C")
        skills_section._sidebar_rendered = True

    # ── Right column: content (manually tracking Y) ──
    cur_y = pdf.margin + 2

    for section in parsed.sections:
        if getattr(section, "_sidebar_rendered", False):
            continue

        # Auto page break check
        if cur_y + 12 > PAGE_H - pdf.margin:
            pdf.add_page()
            cur_y = pdf.margin

        # Section title (green, bold) with underline
        pdf.set_font(family, "B", pdf.fs + 1.5)
        pdf.set_text_color(5, 150, 105)
        pdf.set_xy(right_x, cur_y)
        pdf.cell(right_w, pdf.lh + 3, section.title)
        title_bottom = cur_y + pdf.lh + 3
        pdf.set_draw_color(5, 150, 105)
        pdf.set_line_width(0.4)
        pdf.line(right_x, title_bottom, right_x + right_w, title_bottom)
        cur_y = title_bottom + 3

        # Content lines
        pdf.set_font(family, "", pdf.fs)
        pdf.set_text_color(0, 0, 0)
        for line in section.lines:
            if cur_y + pdf.lh + 1 > PAGE_H - pdf.margin:
                pdf.add_page()
                cur_y = pdf.margin

            text = line.strip()
            if re.match(r"^[-·•]", text):
                text = "· " + re.sub(r"^[-·•]\s*", "", text)
                pdf.set_xy(right_x + 3, cur_y)
                pdf.cell(right_w - 3, pdf.lh + 1, text)
            else:
                pdf.set_xy(right_x, cur_y)
                pdf.cell(right_w, pdf.lh + 1, text)
            cur_y = pdf.get_y()
        cur_y += 3


# ── Template 2: Clean Single Column ────────────────────────
def template_clean_single(pdf: ResumePDF, parsed: ParsedResume, photo_bytes=None):
    """Centered photo + name at top, full-width content below."""
    if photo_bytes:
        photo_x = (pdf.w - 25) / 2
        pdf.embed_photo(photo_bytes, photo_x, pdf.margin + 2, 25, 25)
        pdf.set_y(pdf.margin + 29)
    else:
        pdf.set_y(pdf.margin + 2)

    pdf.set_fs_bold(pdf.fs + 8)
    pdf.cell(0, pdf.lh + 4, parsed.name, align="C", new_x="LMARGIN", new_y="NEXT")

    contact_parts = [v for k, v in parsed.contact.items() if k != "target"]
    if contact_parts:
        pdf.set_fs(pdf.fs - 0.5)
        pdf.cell(0, pdf.lh + 1, "  |  ".join(contact_parts), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    y = pdf.get_y()
    pdf.set_draw_color(5, 150, 105)
    pdf.set_line_width(0.6)
    pdf.line(pdf.margin + 20, y, pdf.w - pdf.margin - 20, y)
    pdf.ln(4)

    for section in parsed.sections:
        pdf.check_page_break(12)
        pdf.write_section_title(section.title)
        for line in section.lines:
            pdf.check_page_break(pdf.lh + 2)
            text = line.strip()
            if re.match(r"^[-·•]", text):
                pdf.write_bullet(re.sub(r"^[-·•]\s*", "", text), indent=5)
            else:
                pdf.write_line(text, indent=0)


# ── Template 3: Modern Cards ───────────────────────────────
def template_modern_cards(pdf: ResumePDF, parsed: ParsedResume, photo_bytes=None):
    """Green header bar, photo top-right, card-style sections."""
    pdf.set_fill_color(5, 150, 105)
    pdf.rect(pdf.margin, pdf.margin, pdf.w - 2 * pdf.margin, 22, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(pdf.margin + 2)
    pdf.set_fs_bold(pdf.fs + 4)
    pdf.cell(0, pdf.lh + 2, parsed.name, align="C", new_x="LMARGIN", new_y="NEXT")
    contact_str = "  |  ".join(v for k, v in parsed.contact.items() if k != "target")
    if contact_str:
        pdf.set_fs(pdf.fs - 1)
        pdf.cell(0, pdf.lh, contact_str, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    if photo_bytes:
        pdf.embed_photo(photo_bytes, pdf.w - pdf.margin - 28, pdf.margin + 2, 22, 22)

    pdf.set_y(pdf.margin + 28)

    for section in parsed.sections:
        pdf.check_page_break(16)
        title_h = pdf.lh + 3
        pdf.set_fill_color(240, 252, 245)
        pdf.rect(pdf.margin, pdf.get_y(), pdf.w - 2 * pdf.margin, title_h, "F")
        pdf.set_fs_bold(pdf.fs + 0.5)
        pdf.set_x(pdf.margin + 3)
        pdf.cell(pdf.w - 2 * pdf.margin - 6, title_h, f"  {section.title}",
                 align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.set_fs()
        for line in section.lines:
            pdf.check_page_break(pdf.lh + 2)
            text = line.strip()
            pdf.set_x(pdf.margin + 5)
            if re.match(r"^[-·•]", text):
                pdf.write_bullet(re.sub(r"^[-·•]\s*", "", text), indent=3)
            else:
                pdf.write_line(text, indent=3)
        pdf.ln(2)


# ── Template 4: Creative Sidebar ───────────────────────────
def template_creative_sidebar(pdf: ResumePDF, parsed: ParsedResume, photo_bytes=None):
    """Dark green sidebar with photo + skills, light content area."""
    sidebar_w = 50
    sidebar_color = (6, 78, 59)
    main_x = pdf.margin + sidebar_w + 6
    main_w = pdf.w - pdf.margin - main_x

    pdf.set_fill_color(*sidebar_color)
    pdf.rect(pdf.margin, pdf.margin, sidebar_w, PAGE_H - 2 * pdf.margin, "F")

    pdf.set_text_color(255, 255, 255)
    sx = pdf.margin + 3
    sw = sidebar_w - 6
    cy = pdf.margin + 4

    if photo_bytes:
        photo_size = sw - 4
        pdf.embed_photo(photo_bytes, sx + 2, cy, photo_size, photo_size)
        cy += photo_size + 4

    pdf.set_fs_bold(pdf.fs + 2)
    pdf.set_xy(sx, cy)
    pdf.multi_cell(sw, pdf.lh + 2, parsed.name, align="C")
    cy = pdf.get_y() + 2

    pdf.set_fs(pdf.fs - 1)
    for key, val in parsed.contact.items():
        if key == "target":
            continue
        pdf.set_xy(sx, cy)
        pdf.multi_cell(sw, pdf.lh + 1, val, align="C")
        cy = pdf.get_y() + 1

    skills_section = next((s for s in parsed.sections if s.key == "skills"), None)
    if skills_section:
        cy += 2
        pdf.set_fs_bold(pdf.fs)
        pdf.set_xy(sx, cy)
        pdf.cell(sw, pdf.lh + 1, "技能", align="C", new_x="LMARGIN", new_y="NEXT")
        cy = pdf.get_y() + 1
        pdf.set_fs(pdf.fs - 1)
        for line in skills_section.lines[:8]:
            pdf.set_xy(sx, cy)
            pdf.cell(sw, pdf.lh + 1, line.strip(), align="C", new_x="LMARGIN", new_y="NEXT")
            cy = pdf.get_y()
        skills_section._sidebar_rendered = True

    pdf.set_text_color(0, 0, 0)
    pdf.set_y(pdf.margin + 2)

    for section in parsed.sections:
        if getattr(section, "_sidebar_rendered", False):
            continue
        pdf.check_page_break(10)
        pdf.set_fs_bold(pdf.fs + 1)
        pdf.set_x(main_x)
        pdf.cell(main_w, pdf.lh + 2, section.title, new_x="LMARGIN", new_y="NEXT")
        y = pdf.get_y()
        pdf.set_draw_color(5, 150, 105)
        pdf.set_line_width(0.3)
        pdf.line(main_x, y, main_x + 30, y)
        pdf.ln(1)
        pdf.set_fs()
        for line in section.lines:
            pdf.check_page_break(pdf.lh + 2)
            text = line.strip()
            if re.match(r"^[-·•]", text):
                pdf.set_x(main_x + 3)
                pdf.write_bullet(re.sub(r"^[-·•]\s*", "", text), indent=0)
            else:
                pdf.set_x(main_x)
                pdf.cell(main_w, pdf.lh + 1, text, align="L", new_x="LMARGIN", new_y="NEXT")


# ── Template 5: Minimal Lines ──────────────────────────────
def template_minimal_lines(pdf: ResumePDF, parsed: ParsedResume, photo_bytes=None):
    """Ultra-clean typography with thin green dividers."""
    header_y = pdf.margin + 2
    if photo_bytes:
        pdf.embed_photo(photo_bytes, pdf.margin + 2, header_y, 18, 18)
        name_x = pdf.margin + 24
    else:
        name_x = pdf.margin

    pdf.set_xy(name_x, header_y)
    pdf.set_fs_bold(pdf.fs + 6)
    pdf.cell(0, pdf.lh + 3, parsed.name, align="L", new_x="LMARGIN", new_y="NEXT")

    contact_str = "  ·  ".join(v for k, v in parsed.contact.items() if k != "target")
    if contact_str:
        pdf.set_x(name_x)
        pdf.set_fs(pdf.fs - 0.5)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, pdf.lh + 1, contact_str, align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

    pdf.ln(3)
    y = pdf.get_y()
    pdf.set_draw_color(5, 150, 105)
    pdf.set_line_width(0.5)
    pdf.line(pdf.margin, y, pdf.w - pdf.margin, y)
    pdf.ln(3)

    for section in parsed.sections:
        pdf.check_page_break(10)
        pdf.set_fs_bold(pdf.fs + 0.5)
        pdf.set_text_color(5, 150, 105)
        pdf.write_line(section.title.upper(), size=pdf.fs + 0.5, bold=True)
        pdf.set_text_color(0, 0, 0)
        for line in section.lines:
            pdf.check_page_break(pdf.lh + 2)
            text = line.strip()
            if re.match(r"^[-·•]", text):
                pdf.write_line(re.sub(r"^[-·•]\s*", "— ", text), indent=4)
            else:
                pdf.write_line(text, indent=2)
        pdf.ln(1)


# ── Template registry ───────────────────────────────────────
TEMPLATES = {
    1: ("经典双栏", "左侧个人信息+照片，右侧经历内容，最通用的简历布局", template_classic_two_column),
    2: ("简洁单栏", "顶部居中头像与姓名，下方通栏排版，适合技术岗位", template_clean_single),
    3: ("现代卡片", "每个模块独立卡片，头像右上角，适合设计/产品岗", template_modern_cards),
    4: ("创意侧边栏", "深色侧边栏展示个人信息与技能，醒目有设计感", template_creative_sidebar),
    5: ("极简线条", "纯文字左对齐排版，细线分割，麦肯锡风格", template_minimal_lines),
}


# ── Main entry point ────────────────────────────────────────
def generate_pdf_resume(
    content: str,
    template_id: int = 1,
    page_limit: int | None = None,
    photo_bytes: bytes | None = None,
) -> bytes:
    """
    Generate a PDF resume.

    Args:
        content: Optimized resume text
        template_id: 1-5 template selection
        page_limit: 1, 2, or None (unlimited)
        photo_bytes: Raw photo file bytes (JPEG/PNG)

    Returns:
        PDF file as bytes
    """
    parsed = parse_resume(content)
    engine = CompressionEngine()

    # Apply compression if page limit specified
    if page_limit is not None:
        parsed, fs, lh, margin = engine.compress(parsed, page_limit)
    else:
        fs, lh, margin = DEFAULT_FONT_SIZE, DEFAULT_LINE_H, DEFAULT_MARGIN

    # Create PDF
    pdf = ResumePDF(font_size=fs, line_h=lh, margin=margin)
    pdf.set_auto_page_break(auto=True, margin=margin)
    pdf.add_page()

    # Render selected template
    if template_id not in TEMPLATES:
        template_id = 1

    _, _, template_fn = TEMPLATES[template_id]
    template_fn(pdf, parsed, photo_bytes)

    # Footer on each page
    for page_num in range(1, pdf.page + 1):
        pdf.page = page_num
        pdf.set_y(-12)
        pdf.set_fs(7)
        pdf.set_text_color(160, 160, 160)
        pdf.cell(0, 8, f"QuickHire AI — 第 {page_num} 页", align="C")

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
