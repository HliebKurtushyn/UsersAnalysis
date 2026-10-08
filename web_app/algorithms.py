def bubble_sort(items):
    result = list(items)
    for end in range(len(result) - 1, 0, -1):
        for index in range(end):
            if result[index] > result[index + 1]:
                result[index], result[index + 1] = result[index + 1], result[index]
    return result


def quick_sort(items):
    if len(items) <= 1:
        return list(items)
    pivot = items[len(items) // 2]
    lower = [item for item in items if item < pivot]
    equal = [item for item in items if item == pivot]
    higher = [item for item in items if item > pivot]
    return quick_sort(lower) + equal + quick_sort(higher)


def linear_search(items, value):
    for index, item in enumerate(items):
        if item == value:
            return index
    return -1


def binary_search(items, value):
    left, right = 0, len(items) - 1
    while left <= right:
        middle = (left + right) // 2
        if items[middle] == value:
            return middle
        if items[middle] < value:
            left = middle + 1
        else:
            right = middle - 1
    return -1
