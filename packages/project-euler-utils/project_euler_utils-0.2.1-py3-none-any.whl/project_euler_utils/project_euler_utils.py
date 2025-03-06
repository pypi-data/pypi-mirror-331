from collections import defaultdict
from .helpers import Collatz

# Problem 2 (Fibonacci)


def sum_of_even_fibonacci_terms(limit: int) -> int:
    """
    Sum of even terms of a fibonacci sequence

    Sum is performed upto the limit provided

    Parameters
    ----------
    limit : int
        limit of the fibonacci sequence


    Returns
    -------
    sum_even : int

    """
    first = 0
    second = 1
    sum_even = 0
    current = 0
    while current < limit:
        current = first + second
        if current % 2 == 0:
            sum_even += current

        first = second
        second = current

    return sum_even


# Problem 3


def largest_prime_factor(n: int):
    """
    Finds the largest prime factor of an integer

    Parameters
    ----------
    n : int


    Returns
    -------
    largest_prime : int

    """
    if n == 0:
        return 0

    i = 2
    while n % i == 0:
        n = n // 2

    i = 3
    while i * i < n:
        while n % i == 0:
            n = n // i
        i = i + 2

    return n if n > 1 else i - 2


"""
Problem 4
A palindromic number reads the same both ways. The largest palindrome made from the product of two 3-digit numbers is 91 * 99 = 9009

Find the largest palindrome made from the product of two 3-digit numbers
"""


def reverse_number(num: int) -> int:
    """
    Reverse a number

    Parameters
    ----------
    num : int


    Returns
    -------
    reverse: int

    """
    reverseNum = 0

    while num:
        ones_place = num % 10
        reverseNum = (reverseNum * 10) + ones_place
        num = num // 10

    return reverseNum


def _get_largest_three_digit_palindrome():
    """
    Largest three digit palindrome

    Parameters
    ----------
    None


    Returns
    -------
    reverse: int

    """
    max_palindrome = float("-inf")
    for i in range(999, 99, -1):
        for j in range(i, 99, -1):
            product = i * j
            if product < max_palindrome:
                continue
            reverse = reverse_number(product)
            if product == reverse:
                max_palindrome = max(max_palindrome, product)

    return max_palindrome


"""
2520 is the smallest number that can be divided by each of the numbers from 1 to 10 without any remainder.

What is the smallest positive number that is evenly divisible by all of the numbers from 1 to 20 ?
"""


def getPrime_less_than_or_equal_to_n(n):
    """
    All prime numbers less than or equal to a number

    Parameters
    ----------
    n : int


    Returns
    -------
    arr : list

    """
    arr = [True for _ in range(n + 1)]
    i = 2
    while i * i < n:
        multiple = 2
        while arr[i] and i * multiple <= n:
            arr[i * multiple] = False
            multiple += 1
        i += 1

    ans = []
    for j in range(2, len(arr)):
        if arr[j]:
            ans.append(j)

    return ans


def smallest_positive_number_divisible_by_all_numbers_till_n(n):
    """
    Finds the LCM of all numbers from 1 to n

    Parameters
    ----------
    n : int


    Returns
    -------
    LCM : int

    """
    primeFactors = getPrime_less_than_or_equal_to_n(n)
    ans = 1
    for value in primeFactors:
        power = 1
        while value**power <= n:
            power += 1
        ans *= value ** (power - 1)

    return ans


# Number of divisors of n
def get_total_positive_divisors(n):
    """
    Count of number of positive divisors of a number inclusive of one

    Parameters
    ----------
    n : int


    Returns
    -------
    count : int

    """
    if n == 0:
        return 0
    if n == 1:
        return 1

    prime_count = defaultdict(int)
    i = 2
    while n % i == 0:
        prime_count[i] = prime_count.get(i, 0) + 1
        n = n // i

    i = 3
    while n > 1:
        while n % i == 0:
            prime_count[i] = prime_count.get(i, 0) + 1
            n = n // i

        i += 2

    divisors = 1
    for prime_factor, count in prime_count.items():
        ways_to_select = count + 1
        divisors = divisors * ways_to_select

    return divisors


def square_sum_difference(n):
    """
    Difference of sum of squares and the sqaure of sum of all digits until n
    Parameters
    ----------
    n : int


    Returns
    -------
    diff = int

    """
    sum_of_n = 0
    sum_of_squares = 0
    for i in range(n + 1):
        sum_of_n += i
        sum_of_squares += i**2

    square_of_sum = sum_of_n**2
    return square_of_sum - sum_of_squares


"""
By listing the first six prime numbers: 2,3,5,7,11, and 13, we can see that the 6th prime is 13.

What is the 10001st prime number?
"""


def get_nth_prime(n):
    """
    Get the nth prime number

    Parameters
    ----------
    n : int


    Returns
    -------
    prime : int

    """

    def _checkPrime(primes, n):
        for i in primes:
            if n % i == 0:
                return False

        return True

    count = 0
    primes = []
    counter = 2
    while count != n:
        if _checkPrime(primes, counter):
            primes.append(counter)
            count += 1
        counter += 1
    return counter - 1


def get_max_product_of_n_adjacent_digits(n: int, number: str):
    """
    Gets the largest product of n adjacent digits in a number

    Parameters
    ----------
    n : int (adjacent)

    number : str


    Returns
    -------
    largest_multiple : int

    """

    number = number.replace("\n", "")

    left = 0
    right = 0
    current_product = 1
    max_product = float("-inf")
    while right < len(number):
        char = number[right]

        if char == "0":
            right += 1
            left = right
            current_product = 1
            continue

        current_product *= int(char)
        if n < right - left + 1:
            leftChar = number[left]
            current_product = current_product // int(leftChar)
            left += 1

        max_product = max(max_product, current_product)
        right += 1

    return max_product


"""
A Pythagorean triplet is a set of three natural numbers, a < b < c , for which,
                a^2 + b^2 = c^2
For example 3^2 + 4^2 = 5^2.

There exists exactly one Pythagorean triplet for which a + b + c = 1000
Find the product abc.
"""


def search_sum_of_pythogorean_triple(s):
    """
    Get the product of pythagorean triplet with a specific sum

    Parameters
    ----------
    s : int


    Returns
    -------
    Assume triplet = a, b, c

    triplet : tuple ((a, b, c), (a * b * c))
    """
    largest_value_of_a = s // 3
    for a in range(1, largest_value_of_a):
        value_of_b = (s * (s - 2 * a)) // (2 * (s - a))
        c = s - value_of_b - a
        if a**2 + value_of_b**2 == c**2:
            return ((a, value_of_b, c), (a * value_of_b * c))
    return -1


def sum_of_primes_until_n(n):
    """
    Sum of all prime numbers until n

    Parameters
    ----------
    n : int


    Returns
    -------
    sum : int

    """

    sieve = [True for _ in range(n)]
    sum_prime = 0
    i = 2
    while i * i < n:
        counter = 2
        while i * counter < n:
            sieve[i * counter] = False
            counter += 1
        i += 1

    for index in range(2, len(sieve)):
        if sieve[index]:
            sum_prime += index

    return sum_prime


def max_product_of_n_adjacent_element_in_grid(grid_str, n):
    """
    Greatest product of n adjacent numbers in the same direction (up, down, left, right, or diagonally) in the grid

    Parameters
    ----------
    grid : str

    n : int


    Returns
    -------
    max_product : int

    """

    if len(grid_str) < n:
        return -1

    # Process input
    grid_line_split = grid_str.split("\n")

    grid = []
    for line in grid_line_split:
        row = [int(num) for num in line.split()]
        grid.append(row)
    rows = len(grid)
    cols = len(grid[0])

    max_product = float("-inf")

    # Row Traversal
    for index in range(len(grid)):
        row = grid[index]
        left = 0
        right = 0
        window_product = 1
        while right < len(row):
            if row[right] == 0:
                right += 1
                left = right
                window_product = 1
                continue

            window_product *= row[right]
            if n < right - left + 1:
                window_product = window_product // row[left]
                left += 1
            max_product = max(max_product, window_product)
            right += 1

    # Col Traversal
    for col in range(len(grid[0])):
        left = 0
        right = 0
        window_product = 1
        while right < len(grid):
            if grid[right][col] == 0:
                right += 1
                left = right
                window_product = 1
                continue

            window_product *= grid[right][col]
            if n < right - left + 1:
                window_product = window_product // grid[left][col]
                left += 1

            max_product = max(max_product, window_product)
            right += 1

    # left to right diagonal traversal
    for index in range(len(grid[0])):
        left_row, left_col = 0, index
        right_row, right_col = 0, index
        window_product = 1
        while right_row < rows and right_col < cols:
            if grid[right_row][right_col] == 0:
                right_row += 1
                right_col += 1
                left_row = right_row
                left_col = right_col
                window_product = 1
                continue

            window_product *= grid[right_row][right_col]
            if n < right_row - left_row + 1:
                window_product = window_product // grid[left_row][left_col]
                left_row += 1
                left_col += 1

            max_product = max(max_product, window_product)
            right_row += 1
            right_col += 1

    # right to left diagonal
    for index in range(len(grid[0]) - 1, -1, -1):
        left_row, left_col = 0, index
        right_row, right_col = 0, index
        window_product = 1
        while 0 <= right_row and right_row < len(grid):
            if grid[right_row][right_col] == 0:
                right_row += 1
                right_col -= 1
                left_row = right_row
                left_col = right_col
                window_product = 1
                continue

            window_product *= grid[right_row][right_col]
            if n < right_row - left_row + 1:
                window_product = window_product // grid[left_row][left_col]
                left_row += 1
                left_col -= 1

            max_product = max(max_product, window_product)
            right_row += 1
            right_col -= 1

    # top to bottom first col
    for index in range(1, len(grid)):
        left_row, left_col = index, 0
        right_row, right_col = index, 0
        window_product = 1
        while right_row < rows and right_col < cols:
            if grid[right_row][right_col] == 0:
                right_row += 1
                right_col += 1
                left_row = right_row
                left_col = right_col
                window_product = 1
                continue

            window_product *= grid[right_row][right_col]
            if n < right_row - left_row + 1:
                window_product = window_product // grid[left_row][left_col]
                left_row += 1
                left_col += 1

            max_product = max(max_product, window_product)
            right_row += 1
            right_col += 1

    # bottom to top last col
    for index in range(len(grid) - 1, -1, -1):
        left_row, left_col = index, len(grid[0]) - 1
        right_row, right_col = index, len(grid[0]) - 1
        window_product = 1
        while 0 <= right_row and 0 <= right_col:
            if grid[right_row][right_col] == 0:
                right_row -= 1
                right_col -= 1
                left_row = right_row
                left_col = right_col
                window_product = 1
                continue

            window_product *= grid[right_row][right_col]
            if n < left_row - right_row + 1:
                window_product = window_product // grid[left_row][left_col]
                left_row -= 1
                left_col -= 1

            max_product = max(max_product, window_product)
            right_row -= 1
            right_col -= 1

    return max_product


"""
The sequence of triangle numbers is generated by adding the natural numbers. So the
th triangle number would be
. The first ten terms would be:

Let us list the factors of the first seven triangle numbers:


We can see that
 is the first triangle number to have over five divisors.

What is the value of the first triangle number to have over five hundred divisors?
"""


def get_nth_triangle_number(n: int) -> int:
    """
    Triangle number is sum of first n natural numbers

    Parameters
    ----------
    n : int


    Returns
    -------
    triangle_number = int
    """
    triangle_number = (n * (n + 1)) // 2

    return triangle_number


def get_count_of_prime_factors(n):
    """
    Returns the count of each prime factor of a number

    Parameters
    ----------
    n : int


    Returns
    -------
    factors = dict (factor, frequency)
    """

    prime_divisors = {}
    i = 2
    while n % i == 0:
        prime_divisors[i] = prime_divisors.get(i, 0) + 1
        n = n // 2
    i = 3
    while n > 1:
        while n % i == 0:
            prime_divisors[i] = prime_divisors.get(i, 0) + 1
            n = n // i
        i += 2
    return prime_divisors


def first_triangle_number_to_have_n_divisors(n):
    """
    Smallest triangle number with n total divisors

    Parameters
    ----------
    n : int


    Returns
    -------
    number : int

    """

    counter = 1
    while True:
        triangle_number = get_nth_triangle_number(counter)
        current_divisors = get_total_positive_divisors(triangle_number)
        if n < current_divisors:
            return triangle_number
        counter += 1


# Collatz number Problem 14


def collatz_number():
    collatz = Collatz()

    for i in range(1000000, 0, -1):
        current_collatz = collatz.get_collatz(i)

    max_chain = float("-inf")
    max_chain_number = 0
    for num, length in collatz.lengths.items():
        if max_chain < length:
            max_chain = length
            max_chain_number = num
