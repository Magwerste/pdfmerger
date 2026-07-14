import pytest

from pdfmerger.page_range import InvalidPageRangeError, PageRange


def test_parse_all():
    assert PageRange.parse("all").is_all


def test_parse_empty_is_all():
    assert PageRange.parse("").is_all


def test_parse_single_pages():
    assert PageRange.parse("1,3,5").resolve(5) == [0, 2, 4]


def test_parse_range():
    assert PageRange.parse("2-4").resolve(5) == [1, 2, 3]


def test_parse_mixed_list_and_range():
    assert PageRange.parse("1,3-5").resolve(5) == [0, 2, 3, 4]


def test_duplicate_pages_are_deduplicated():
    assert PageRange.parse("1,1,2-3").resolve(5) == [0, 1, 2]


@pytest.mark.parametrize("text", ["0", "-1", "abc", "3-1"])
def test_invalid_ranges_raise(text):
    with pytest.raises(InvalidPageRangeError):
        PageRange.parse(text)


def test_blank_entries_are_ignored():
    assert PageRange.parse("1,,2").resolve(5) == [0, 1]


def test_resolve_out_of_bounds_raises():
    with pytest.raises(InvalidPageRangeError):
        PageRange.parse("10").resolve(5)


def test_resolve_all_uses_page_count():
    assert PageRange.all_pages().resolve(3) == [0, 1, 2]
