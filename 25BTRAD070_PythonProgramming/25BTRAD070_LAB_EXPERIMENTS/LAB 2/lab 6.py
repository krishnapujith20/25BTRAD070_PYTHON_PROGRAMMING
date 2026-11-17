def prime_number(n):
    if n < 2:
        return False

    for i in range(2, n):
        if n % i == 0:
            return False

    return True


num = int(input("Enter a number: "))

if prime_number(num):
    print("Prime number")
else:
    print("Not a prime number")