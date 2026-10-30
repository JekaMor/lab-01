import inspect
import logging

from findex.corpus import Document, iter_documents


def test_is_generator_function():
    assert inspect.isgeneratorfunction(iter_documents)


def test_yields_documents_from_nested_txt_files(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "sub" / "b.txt").write_text("бета", encoding="utf-8")
    (tmp_path / "ignored.md").write_text("nope", encoding="utf-8")

    docs = list(iter_documents(tmp_path))

    assert {d.text for d in docs} == {"alpha", "бета"}
    assert sorted(d.doc_id for d in docs) == [0, 1]
    assert all(isinstance(d, Document) for d in docs)
    assert {d.path.name for d in docs} == {"a.txt", "b.txt"}


def test_bad_encoding_is_logged_and_does_not_stop_the_stream(tmp_path, caplog):
    (tmp_path / "bad.txt").write_bytes(b"ok \xff\xfe broken")
    (tmp_path / "good.txt").write_text("fine", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="findex.corpus"):
        docs = list(iter_documents(tmp_path))

    assert len(docs) == 2
    assert any("bad.txt" in r.getMessage() for r in caplog.records)
    assert "fine" in {d.text for d in docs}


def test_file_vanishing_mid_stream_is_skipped(tmp_path, caplog):
    for name in ("a", "b"):
        (tmp_path / f"{name}.txt").write_text(name, encoding="utf-8")
    gen = iter_documents(tmp_path)
    first = next(gen)
    for p in tmp_path.glob("*.txt"):
        if p != first.path:
            p.unlink()

    with caplog.at_level(logging.WARNING, logger="findex.corpus"):
        assert list(gen) == []

    assert any("unreadable" in r.getMessage() for r in caplog.records)
