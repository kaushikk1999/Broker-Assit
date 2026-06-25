"""Phase 4 chunker — deterministic word-window chunking with overlap."""
from app.ingestion.chunker import chunk_text, normalize_text


def test_empty_text_yields_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\t  ") == []


def test_short_text_is_single_chunk():
    out = chunk_text("NALCO quarterly results rose", chunk_size=50, overlap=10)
    assert out == ["NALCO quarterly results rose"]


def test_long_text_splits_into_overlapping_windows():
    words = [f"w{i}" for i in range(25)]
    out = chunk_text(" ".join(words), chunk_size=10, overlap=3)
    assert len(out) > 1
    # step = size - overlap = 7, so the 2nd window starts at word index 7
    assert out[0].split()[0] == "w0"
    assert out[1].split()[0] == "w7"
    # every original word is covered by at least one window
    covered = {w for chunk in out for w in chunk.split()}
    assert covered == set(words)


def test_overlap_is_clamped_below_chunk_size():
    # overlap >= size would stall the window; it must be clamped so the window still advances
    out = chunk_text(" ".join(f"w{i}" for i in range(20)), chunk_size=5, overlap=99)
    assert len(out) >= 4


def test_chunking_is_deterministic():
    text = "alumina realisations drove higher revenue and net profit this quarter " * 20
    assert chunk_text(text, chunk_size=8, overlap=2) == chunk_text(text, chunk_size=8, overlap=2)


def test_normalize_collapses_whitespace():
    assert normalize_text("a\n\n b\t c   d") == "a b c d"
