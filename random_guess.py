import random
import os

number = random.randint(1, 10)
guess = input("make you guess from 1 to 10: ")
guess = int(guess)

if guess == number:
    print("You won!")
else:
    print("You are cooked! 😂😂")
    print(f"correct number is: {number}")