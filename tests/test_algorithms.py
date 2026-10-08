from web_app.algorithms import binary_search, bubble_sort, quick_sort


def test_sorting_algorithms():
    values = [3, 1, 2]
    assert bubble_sort(values) == [1, 2, 3]
    assert quick_sort(values) == [1, 2, 3]


def test_binary_search():
    assert binary_search([1, 2, 3], 2) == 1
    assert binary_search([1, 2, 3], 4) == -1
