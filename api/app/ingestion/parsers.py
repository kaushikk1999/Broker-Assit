"""Content parsers — raw source payload -> clean plain text (deterministic, offline for fixtures).

HTML and plain text/markdown are parsed with the stdlib only, so the fixtures path needs no extra
dependencies. Binary office formats (PDF/DOCX/PPTX/XLSX) are parsed with optional libraries that are
only imported on the live path; if the dependency is missing a ``ParserDependencyError`` is raised
(never on the credential-free fixtures path)."""
from __future__ import annotations

import re
from html.parser import HTMLParser


class ParserDependencyError(RuntimeError):
    """A binary parser (PDF/DOCX/PPTX/XLSX) needs an optional dependency that is not installed."""


class UnsupportedContentType(ValueError):
    """No parser is registered for the given content type."""


_WS = re.compile(r"\s+")
_DROP_TAGS = {"script", "style", "head", "noscript"}
_BLOCK_TAGS = {"p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article"}


class _TextExtractor(HTMLParser):
    """Collect visible text, dropping script/style and inserting breaks at block boundaries."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _DROP_TAGS:
            self._skip_depth += 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def parse_html(content: str) -> str:
    p = _TextExtractor()
    p.feed(content or "")
    return _WS.sub(" ", p.text()).strip()


def parse_text(content: str) -> str:
    return _WS.sub(" ", content or "").strip()


def _parse_pdf(raw: bytes) -> str:  # pragma: no cover - live path only
    try:
        from pypdf import PdfReader  # optional dep (requirements-ingest.txt)
        from io import BytesIO
    except ImportError as e:
        raise ParserDependencyError("PDF parsing needs 'pypdf' (pip install -r requirements-ingest.txt)") from e
    reader = PdfReader(BytesIO(raw))
    return _WS.sub(" ", " ".join((page.extract_text() or "") for page in reader.pages)).strip()


def _parse_docx(raw: bytes) -> str:  # pragma: no cover - live path only
    try:
        import docx  # python-docx (optional dep)
        from io import BytesIO
    except ImportError as e:
        raise ParserDependencyError("DOCX parsing needs 'python-docx'") from e
    doc = docx.Document(BytesIO(raw))
    return _WS.sub(" ", " ".join(p.text for p in doc.paragraphs)).strip()


# content-type prefix -> text parser. Binary parsers receive bytes; text parsers receive str.
_TEXT_PARSERS = {
    "text/html": parse_html,
    "application/xhtml": parse_html,
    "text/plain": parse_text,
    "text/markdown": parse_text,
    "text/": parse_text,
}
_BINARY_PARSERS = {
    "application/pdf": _parse_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml": _parse_docx,
}


def parse(content, content_type: str = "text/html") -> str:
    """Dispatch on content type, returning clean plain text. ``content`` is ``str`` for text formats
    and ``bytes`` for binary formats."""
    ct = (content_type or "text/html").split(";")[0].strip().lower()
    for prefix, fn in _TEXT_PARSERS.items():
        if ct.startswith(prefix):
            return fn(content if isinstance(content, str) else content.decode("utf-8", "ignore"))
    for prefix, fn in _BINARY_PARSERS.items():
        if ct.startswith(prefix):
            return fn(content if isinstance(content, bytes) else str(content).encode())
    raise UnsupportedContentType(f"no parser for content type {content_type!r}")
