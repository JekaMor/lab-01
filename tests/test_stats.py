from findex.stats import eager_stats, lazy_stats, main


def make_corpus(tmp_path):
    (tmp_path / "a.txt").write_text("the cat and the dog", encoding="utf-8")
    (tmp_path / "b.txt").write_text("The end. Кіт і кіт!", encoding="utf-8")
    return tmp_path


def test_lazy_stats_counts(tmp_path):
    stats = lazy_stats(make_corpus(tmp_path), top=2)

    assert stats.documents == 2
    assert stats.tokens == 10
    assert stats.vocabulary == 7
    assert stats.top[0] == ("the", 3)
    assert len(stats.top) == 2


def test_limit_takes_first_n_documents(tmp_path):
    stats = lazy_stats(make_corpus(tmp_path), limit=1)

    assert stats.documents == 1


def test_eager_matches_lazy(tmp_path):
    root = make_corpus(tmp_path)

    assert eager_stats(root, top=50) == lazy_stats(root, top=50)


def test_main_prints_report(tmp_path, capsys):
    root = make_corpus(tmp_path)

    main([str(root), "--top", "3"])

    out = capsys.readouterr().out
    for needle in ("documents", "tokens", "vocabulary", "the", "elapsed", "peak memory"):
        assert needle in out


def test_main_eager_flag(tmp_path, capsys):
    main([str(make_corpus(tmp_path)), "--eager"])

    assert "eager" in capsys.readouterr().out
