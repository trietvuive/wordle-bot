#!/usr/bin/env python3
"""
Wordle Game Simulator - Command Line Version
A classic Wordle game where you have 6 attempts to guess a 5-letter word.
"""

import random
import sys
import os
from enum import Enum
from typing import List, Tuple, Dict, Set, Optional


class Color(Enum):
    GREEN = "green"  # Correct letter, correct position
    YELLOW = "yellow"  # Correct letter, wrong position
    GRAY = "gray"  # Letter not in word


class Colors:
    GREEN = "\033[92m"  # Correct letter, correct position
    YELLOW = "\033[93m"  # Correct letter, wrong position
    GRAY = "\033[90m"  # Letter not in word
    RESET = "\033[0m"  # Reset color
    BOLD = "\033[1m"
    WHITE = "\033[97m"


CLEAR_LINE = "\033[2K"
MOVE_UP = "\033[1A"
CURSOR_HOME = "\033[0G"
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DICTIONARY_DIR = os.path.join(os.path.dirname(_SCRIPT_DIR), "dictionary")
WORDLE_LA_FILE = os.path.join(_DICTIONARY_DIR, "wordle-La.txt")
WORDLE_TA_FILE = os.path.join(_DICTIONARY_DIR, "wordle-Ta.txt")


class WordleGame:
    """Encapsulates the state and logic of a Wordle game."""

    def __init__(self, dictionary_dir: str = None):
        """
        Initialize a new Wordle game.

        Args:
            dictionary_dir: Directory containing word lists. If None, uses default paths.
        """
        la_words = self._load_word_list(WORDLE_LA_FILE)
        ta_words = self._load_word_list(WORDLE_TA_FILE)
        self.target = random.choice(la_words).upper()
        self.valid_guesses: Set[str] = set(la_words + ta_words)
        self.attempts = 0
        self.max_attempts = 6
        self.guessed_letters: Dict[str, Color] = {}
        self.all_guesses: List[List[Tuple[str, Color]]] = []
        self.lines_printed = 0
        self.won = False

    @staticmethod
    def _load_word_list(filename: str) -> List[str]:
        """Load the word list from file."""
        try:
            with open(filename, "r") as f:
                words = [line.strip().upper() for line in f if line.strip()]
            return words
        except FileNotFoundError:
            print(f"Error: {filename} not found!")
            sys.exit(1)

    def _get_feedback(self, guess: str) -> List[Tuple[str, Color]]:
        """
        Generate feedback for a guess.
        Returns a list of tuples: (letter, color)
        """
        feedback: List[Tuple[str, Optional[Color]]] = []
        target_list = list(self.target)
        guess_list = list(guess)

        for i in range(len(guess_list)):
            if guess_list[i] == target_list[i]:
                feedback.append((guess_list[i], Color.GREEN))
                target_list[i] = None
                guess_list[i] = None
            else:
                feedback.append((guess_list[i], None))

        for i in range(len(guess_list)):
            if guess_list[i] is not None:
                if guess_list[i] in target_list:
                    feedback[i] = (guess_list[i], Color.YELLOW)
                    target_list[target_list.index(guess_list[i])] = None
                else:
                    feedback[i] = (guess_list[i], Color.GRAY)

        return feedback  # type: ignore

    def is_valid_guess(self, guess: str) -> bool:
        """Check if the guess is valid (5 letters and in valid guesses set)."""
        if len(guess) != 5:
            return False
        if not guess.isalpha():
            return False
        return guess.upper() in self.valid_guesses

    def _update_keyboard_state(self, feedback: List[Tuple[str, Color]]):
        """Update the keyboard state based on feedback."""
        for letter, color in feedback:
            letter_upper = letter.upper()
            if letter_upper not in self.guessed_letters or color == Color.GREEN:
                self.guessed_letters[letter_upper] = color

    @staticmethod
    def _get_ansi_color(color: Color, bold: bool = False) -> str:
        """Get ANSI color code for a Color enum value."""
        color_map = {
            Color.GREEN: Colors.GREEN,
            Color.YELLOW: Colors.YELLOW,
            Color.GRAY: Colors.GRAY,
        }
        ansi_color = color_map[color]
        return f"{Colors.BOLD}{ansi_color}" if bold else ansi_color

    def _display_header(self) -> int:
        """Display the game header. Returns number of lines printed."""
        print(f"{Colors.BOLD}=== WORDLE ==={Colors.RESET}")
        print("Guess the 5-letter word in 6 attempts!")
        print("Green = correct letter, correct position")
        print("Yellow = correct letter, wrong position")
        print("Gray = letter not in word")
        print()
        return 6

    def _display_guesses(self) -> int:
        """Display all previous guesses. Returns number of lines printed."""
        lines = 0
        for feedback in self.all_guesses:
            for letter, color in feedback:
                ansi_color = self._get_ansi_color(color, bold=True)
                print(f"{ansi_color}{letter}{Colors.RESET}", end=" ")
            print()
            lines += 1
        return lines

    def _display_keyboard(self) -> int:
        """Display the keyboard state. Returns number of lines printed."""
        keyboard_rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"],
        ]

        print("\nKeyboard:")
        lines = 1
        for row in keyboard_rows:
            for letter in row:
                if letter in self.guessed_letters:
                    color = self.guessed_letters[letter]
                    ansi_color = self._get_ansi_color(color)
                    print(f"{ansi_color}{letter}{Colors.RESET}", end=" ")
                else:
                    print(f"{Colors.WHITE}{letter}{Colors.RESET}", end=" ")
            print()
            lines += 1
        return lines

    def _clear_display(self):
        """Clear previous display by moving up and clearing lines."""
        if self.lines_printed > 0:
            for _ in range(self.lines_printed):
                print(f"{CLEAR_LINE}{MOVE_UP}", end="")
        print(f"{CURSOR_HOME}", end="")

    def display_game_state(self):
        """
        Display the entire game state: all previous guesses and keyboard.
        This function overwrites previous output.
        """
        self._clear_display()

        lines = 0
        lines += self._display_header()
        lines += self._display_guesses()
        lines += self._display_keyboard()

        sys.stdout.flush()
        self.lines_printed = lines

    def make_guess(self, guess: str) -> bool:
        """
        Process a guess and update game state.

        Args:
            guess: The word to guess

        Returns:
            True if the guess was valid, False otherwise
        """
        guess = guess.strip().upper()

        if not self.is_valid_guess(guess):
            return False

        feedback = self._get_feedback(guess)
        self.all_guesses.append(feedback)
        self._update_keyboard_state(feedback)

        if guess == self.target:
            self.won = True

        self.attempts += 1
        return True

    def is_won(self) -> bool:
        """Check if the game has been won."""
        return self.won

    def is_game_over(self) -> bool:
        """Check if the game is over (won or out of attempts)."""
        return self.won or self.attempts >= self.max_attempts

    def play(self):
        """Main game loop."""
        self.display_game_state()

        while not self.is_game_over():
            print(f"\nAttempt {self.attempts + 1}/{self.max_attempts}")
            guess = input("Enter your guess: ").strip().upper()

            if not self.make_guess(guess):
                print(f"{CLEAR_LINE}{MOVE_UP}{CLEAR_LINE}{MOVE_UP}{CLEAR_LINE}", end="")
                print("Invalid guess! Please enter a valid 5-letter word.")
                sys.stdout.flush()
                continue

            print(f"{CLEAR_LINE}{MOVE_UP}{CLEAR_LINE}{MOVE_UP}", end="")
            self.display_game_state()

            if self.is_won():
                print(
                    f"\n{Colors.GREEN}{Colors.BOLD}Congratulations! You won!{Colors.RESET}"
                )
                print(f"The word was: {Colors.BOLD}{self.target}{Colors.RESET}")
                return

        if not self.won:
            print(f"\n{Colors.GRAY}Game Over!{Colors.RESET}")
            print(f"The word was: {Colors.BOLD}{self.target}{Colors.RESET}")


def play_wordle():
    """Main entry point to play a Wordle game."""
    game = WordleGame()
    game.play()


if __name__ == "__main__":
    try:
        play_wordle()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GRAY}Game interrupted. Goodbye!{Colors.RESET}")
        sys.exit(0)