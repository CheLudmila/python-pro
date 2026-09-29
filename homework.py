# 1. Рядки

def string_length(text):
    return len(text)


def concatenate_strings(first, second):
    return first + second


# 2. Числа

def square(number):
    return number ** 2


def add_numbers(first, second):
    return first + second


def divide_numbers(first: int, second: int):
    if second == 0:
        raise ValueError("На нуль ділити не можна")
    return first // second, first % second


# 3. Списки

def average(numbers):
    if not numbers:
        raise ValueError("Список не повинен бути порожнім")
    return sum(numbers) / len(numbers)


def common_elements(first, second):
    result = []
    for element in first:
        if element in second and element not in result:
            result.append(element)
    return result


# 4. Словники

def print_keys(dictionary):
    for key in dictionary:
        print(key)


def merge_dictionaries(first, second):
    result = first.copy()
    result.update(second)
    return result


# 5. Множини

def union_sets(first, second):
    return first | second


def is_subset(first, second):
    return first.issubset(second)


# 6. Умовні вирази та цикли

def print_parity(number):
    if number % 2 == 0:
        print("Парне")
    else:
        print("Непарне")


def even_numbers(numbers):
    result = []
    for number in numbers:
        if number % 2 == 0:
            result.append(number)
    return result


# 7. Лямбда-функція

parity = lambda number: "парне" if number % 2 == 0 else "не парне"


# Приклади використання

if __name__ == "__main__":
    print(string_length("Привіт"))
    print(concatenate_strings("Привіт, ", "світе!"))

    print(square(5))
    print(add_numbers(3, 2.5))
    print(divide_numbers(17, 5))

    print(average([10, 20, 30]))
    print(common_elements([1, 2, 2, 3], [2, 3, 4]))

    print_keys({"name": "Олена", "age": 25})
    print(merge_dictionaries({"a": 1}, {"b": 2}))

    print(union_sets({1, 2}, {2, 3}))
    print(is_subset({1, 2}, {1, 2, 3}))

    print_parity(4)
    print(even_numbers([1, 2, 3, 4, 5, 6]))

    print(parity(8))
    print(parity(7))
