#!/usr/bin/env python3
"""
Wordle Game Simulator - Command Line Version
A classic Wordle game where you have 6 attempts to guess a 5-letter word.
"""

import random
import sys
from typing import List, Tuple

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'  # Correct letter, correct position
    YELLOW = '\033[93m'  # Correct letter, wrong position
    GRAY = '\033[90m'   # Letter not in word
    RESET = '\033[0m'   # Reset color
    BOLD = '\033[1m'
    WHITE = '\033[97m'

def load_word_list(filename: str) -> List[str]:
    """Load the word list from file."""
    try:
        with open(filename, 'r') as f:
            words = [line.strip().upper() for line in f if line.strip()]
        return words
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        sys.exit(1)

def get_feedback(guess: str, target: str) -> List[Tuple[str, str]]:
    """
    Generate feedback for a guess.
    Returns a list of tuples: (letter, color_code)
    color_code: 'green', 'yellow', or 'gray'
    """
    feedback = []
    target_list = list(target)
    guess_list = list(guess)
    
    # First pass: mark exact matches (green)
    for i in range(len(guess_list)):
        if guess_list[i] == target_list[i]:
            feedback.append((guess_list[i], 'green'))
            target_list[i] = None  # Mark as used
            guess_list[i] = None   # Mark as processed
        else:
            feedback.append((guess_list[i], None))  # Placeholder
    
    # Second pass: mark correct letters in wrong position (yellow)
    for i in range(len(guess_list)):
        if guess_list[i] is not None:  # Not already processed
            if guess_list[i] in target_list:
                feedback[i] = (guess_list[i], 'yellow')
                # Remove first occurrence from target_list
                target_list[target_list.index(guess_list[i])] = None
            else:
                feedback[i] = (guess_list[i], 'gray')
    
    return feedback

def display_guess(feedback: List[Tuple[str, str]]):
    """Display a guess with color-coded feedback."""
    for letter, color in feedback:
        if color == 'green':
            print(f"{Colors.GREEN}{Colors.BOLD}{letter}{Colors.RESET}", end=' ')
        elif color == 'yellow':
            print(f"{Colors.YELLOW}{Colors.BOLD}{letter}{Colors.RESET}", end=' ')
        else:  # gray
            print(f"{Colors.GRAY}{letter}{Colors.RESET}", end=' ')
    print()  # New line

def display_keyboard_state(guessed_letters: dict):
    """Display the keyboard state showing which letters have been used."""
    keyboard_rows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ]
    
    print("\nKeyboard:")
    for row in keyboard_rows:
        for letter in row:
            if letter in guessed_letters:
                color = guessed_letters[letter]
                if color == 'green':
                    print(f"{Colors.GREEN}{letter}{Colors.RESET}", end=' ')
                elif color == 'yellow':
                    print(f"{Colors.YELLOW}{letter}{Colors.RESET}", end=' ')
                else:
                    print(f"{Colors.GRAY}{letter}{Colors.RESET}", end=' ')
            else:
                print(f"{Colors.WHITE}{letter}{Colors.RESET}", end=' ')
        print()

def update_keyboard_state(guessed_letters: dict, feedback: List[Tuple[str, str]]):
    """Update the keyboard state based on feedback."""
    for letter, color in feedback:
        letter_upper = letter.upper()
        # Only update if we haven't seen this letter, or if it's now green
        # (green overrides yellow/gray)
        if letter_upper not in guessed_letters or color == 'green':
            guessed_letters[letter_upper] = color

def is_valid_guess(guess: str, valid_guesses: set) -> bool:
    """Check if the guess is valid (5 letters and in valid guesses set)."""
    if len(guess) != 5:
        return False
    if not guess.isalpha():
        return False
    return guess.upper() in valid_guesses

def play_wordle():
    """Main game loop."""
    print(f"{Colors.BOLD}=== WORDLE ==={Colors.RESET}\n")
    print("Guess the 5-letter word in 6 attempts!")
    print("Green = correct letter, correct position")
    print("Yellow = correct letter, wrong position")
    print("Gray = letter not in word\n")
    
    # Load word lists
    # La words: can be guessed AND can be the word of the day
    la_words = load_word_list("wordle-La.txt")
    # Ta words: can be guessed but are never selected as the word of the day
    ta_words = load_word_list("wordle-Ta.txt")
    
    # Target word is selected only from La words
    target = random.choice(la_words).upper()
    
    # Valid guesses include both La and Ta words
    valid_guesses = set(la_words + ta_words)
    
    attempts = 0
    max_attempts = 6
    guessed_letters = {}
    
    while attempts < max_attempts:
        print(f"\nAttempt {attempts + 1}/{max_attempts}")
        guess = input("Enter your guess: ").strip().upper()
        
        # Validate guess
        if not is_valid_guess(guess, valid_guesses):
            print("Invalid guess! Please enter a valid 5-letter word.")
            continue
        
        # Get feedback
        feedback = get_feedback(guess, target)
        display_guess(feedback)
        
        # Update keyboard state
        update_keyboard_state(guessed_letters, feedback)
        display_keyboard_state(guessed_letters)
        
        # Check for win
        if guess == target:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Congratulations! You won!{Colors.RESET}")
            print(f"The word was: {Colors.BOLD}{target}{Colors.RESET}")
            return
        
        attempts += 1
    
    # Game over
    print(f"\n{Colors.GRAY}Game Over!{Colors.RESET}")
    print(f"The word was: {Colors.BOLD}{target}{Colors.RESET}")

if __name__ == "__main__":
    try:
        play_wordle()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GRAY}Game interrupted. Goodbye!{Colors.RESET}")
        sys.exit(0)

