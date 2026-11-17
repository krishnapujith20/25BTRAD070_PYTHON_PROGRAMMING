import random

def guessing_game():
    number = random.randint(1, 10)

    while True:
        guess = int(input("Enter your guess (1-10): "))

        if guess == number:
            print("Correct! You guessed the number.")
            break
        elif guess < number:
            print("Too low! Try again.")
        else:
            print("Too high! Try again.")

guessing_game()