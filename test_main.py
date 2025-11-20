import os
from datetime import date
import pytest

from main import parse_date, parse_float, RBTree, load_data


def test_parse_date_valid():
    assert parse_date("2021-12-31") == date(2021, 12, 31)


def test_parse_date_invalid_and_empty():
    assert parse_date("") is None
    assert parse_date("2021/12/31") is None
    assert parse_date("not-a-date") is None


def test_parse_float_variants():
    assert parse_float("3.5") == 3.5
    assert parse_float("10") == 10.0
    assert parse_float(None) is None
    assert parse_float("abc") is None


def test_rbtree_insert_and_range_ids():
    t = RBTree(float)
    t.insert(1.0, "A")
    t.insert(2.0, "B")
    t.insert(1.0, "C")
    all_ids = t.range_ids(None, None)
    assert all_ids == {"A", "B", "C"}
    only_one = t.range_ids(1.0, 1.0)
    assert only_one == {"A", "C"}
    upper = t.range_ids(None, 1.5)
    assert upper == {"A", "C"}


def test_load_data_basic():
    root = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(root, "horror_movies.csv")
    by_id, idx_date, idx_vote = load_data(csv_path)
    assert isinstance(by_id, dict)
    assert len(by_id) > 0

    sample = None
    for rec in by_id.values():
        assert "id" in rec
        assert "title" in rec
        assert "release_date" in rec
        assert "vote_average" in rec
        if rec["release_date"] is not None and rec["vote_average"] is not None:
            sample = rec
    assert sample is not None

    ids_date_all = idx_date.range_ids(None, None)
    expected_date_ids = {r["id"] for r in by_id.values() if r["release_date"] is not None}
    assert ids_date_all == expected_date_ids

    ids_vote_all = idx_vote.range_ids(None, None)
    expected_vote_ids = {r["id"] for r in by_id.values() if r["vote_average"] is not None}
    assert ids_vote_all == expected_vote_ids

    ids_for_date = idx_date.range_ids(sample["release_date"], sample["release_date"])
    assert sample["id"] in ids_for_date

    ids_for_vote = idx_vote.range_ids(sample["vote_average"], sample["vote_average"])
    assert sample["id"] in ids_for_vote


def test_load_data_missing_file():
    with pytest.raises(FileNotFoundError):
        load_data("no_such_file.csv")