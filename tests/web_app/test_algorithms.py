import pytest

from web_app.algorithms import (
    binary_search,
    bubble_sort,
    linear_search,
    quick_sort,
)


@pytest.mark.parametrize("sort_function", [bubble_sort, quick_sort])
@pytest.mark.parametrize(
    "values",
    [
        [],
        [1, 2, 3],
        [3, 1, 2, 2, 1],
    ],
)
def test_sorting_algorithms_edge_cases(sort_function, values):
    assert sort_function(values) == sorted(values)


def test_sorting_algorithms_do_not_modify_input():
    values = [3, 1, 2]

    bubble_sort(values)
    quick_sort(values)

    assert values == [3, 1, 2]


@pytest.mark.parametrize(
    ("search_function", "values", "value", "expected"),
    [
        (linear_search, [], 1, -1),
        (linear_search, [1, 2, 3], 1, 0),
        (linear_search, [1, 2, 3], 3, 2),
        (linear_search, [1, 2, 3], 4, -1),
        (binary_search, [], 1, -1),
        (binary_search, [1, 2, 3], 1, 0),
        (binary_search, [1, 2, 3], 3, 2),
        (binary_search, [1, 2, 3], 4, -1),
    ],
)
def test_search_algorithms_boundaries_and_missing_values(
    search_function,
    values,
    value,
    expected,
):
    assert search_function(values, value) == expected
