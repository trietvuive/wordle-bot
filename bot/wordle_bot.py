#!/usr/bin/env python3
"""
Optimal Wordle Bot using Information Theory and Decision Trees.

This bot uses entropy-based decision making to choose guesses that maximize
information gain, minimizing the expected number of remaining possible words.
"""

import math
import sys
import os
import threading
import time
from collections import Counter
from typing import List, Set, Tuple, Dict, Optional

# Add parent directory to path to import wordle_game
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent_dir)

from game.wordle_game import WordleGame, Color

# Get file paths
_GAME_DIR = os.path.join(_parent_dir, "game")
_DICTIONARY_DIR = os.path.join(_parent_dir, "dictionary")
WORDLE_LA_FILE = os.path.join(_DICTIONARY_DIR, "wordle-La.txt")
WORDLE_TA_FILE = os.path.join(_DICTIONARY_DIR, "wordle-Ta.txt")


class WordleBot:
    """Optimal Wordle bot using information theory."""

    def __init__(self):
        """Initialize the bot with word lists."""
        self.la_words = self._load_word_list(WORDLE_LA_FILE)
        self.ta_words = self._load_word_list(WORDLE_TA_FILE)
        self.all_words = [w.upper() for w in self.la_words + self.ta_words]
        self.possible_words = set(self.la_words)
        self._spinner_active = False
        self._spinner_thread = None
        self._game_helper = WordleGame()

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

    def _get_feedback(self, guess: str, target: str) -> List[Tuple[str, Color]]:
        """
        Generate feedback for a guess against a target.
        Returns a list of tuples: (letter, color)
        Uses WordleGame's feedback method.
        """
        original_target = self._game_helper.target
        self._game_helper.target = target.upper()
        feedback = self._game_helper._get_feedback(guess.upper())
        self._game_helper.target = original_target
        return feedback

    def _filter_words(
        self, words: Set[str], guess: str, feedback: List[Tuple[str, Color]]
    ) -> Set[str]:
        """Filter possible words based on feedback from a guess."""
        filtered = set()
        for word in words:
            if self._matches_feedback(word, guess, feedback):
                filtered.add(word)
        return filtered

    def _matches_feedback(
        self, word: str, guess: str, feedback: List[Tuple[str, Color]]
    ) -> bool:
        """Check if a word matches the given feedback pattern."""
        expected_feedback = self._get_feedback(guess, word)
        return expected_feedback == feedback

    def _calculate_entropy(self, guess: str, possible_words: Set[str]) -> float:
        """
        Calculate the entropy (information gain) of a guess.
        Higher entropy means more information gained.
        """
        if not possible_words:
            return 0.0

        feedback_counts: Dict[Tuple, int] = {}
        for target in possible_words:
            feedback = tuple(self._get_feedback(guess, target))
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1

        total = len(possible_words)
        entropy = 0.0
        for count in feedback_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _calculate_expected_remaining(
        self, guess: str, possible_words: Set[str]
    ) -> float:
        """
        Calculate the expected number of remaining words after a guess.
        Lower is better.
        """
        if not possible_words:
            return 0.0

        feedback_counts: Dict[Tuple, int] = {}
        for target in possible_words:
            feedback = tuple(self._get_feedback(guess, target))
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1

        total = len(possible_words)
        expected = 0.0
        for count in feedback_counts.values():
            probability = count / total
            expected += probability * count

        return expected

    def _show_spinner(self):
        """Show a loading spinner while computing."""
        spinner_chars = "|/-\\"
        i = 0
        while self._spinner_active:
            print(
                f"\rComputing optimal guess... {spinner_chars[i % len(spinner_chars)]}",
                end="",
                flush=True,
            )
            time.sleep(0.1)
            i += 1
        print("\r" + " " * 30 + "\r", end="", flush=True)

    def _choose_optimal_guess(
        self,
        possible_words: Set[str],
        valid_guesses: Set[str],
        show_spinner: bool = True,
    ) -> str:
        """
        Choose the optimal guess using information theory.
        Prioritizes guesses that minimize expected remaining words.
        """
        if len(possible_words) == 1:
            return list(possible_words)[0]

        if show_spinner:
            self._spinner_active = True
            self._spinner_thread = threading.Thread(
                target=self._show_spinner, daemon=True
            )
            self._spinner_thread.start()

        try:
            if len(possible_words) <= 2:
                candidates = list(possible_words)
            else:
                candidates = list(possible_words) + list(valid_guesses)
                seen = set()
                candidates = [w for w in candidates if not (w in seen or seen.add(w))]

            best_guess = None
            best_score = float("inf")

            for guess in candidates:
                expected_remaining = self._calculate_expected_remaining(
                    guess, possible_words
                )
                bonus = 0 if guess in possible_words else 0.5
                score = expected_remaining + bonus

                if score < best_score:
                    best_score = score
                    best_guess = guess

            return best_guess or candidates[0]
        finally:
            if show_spinner:
                self._spinner_active = False
                if self._spinner_thread:
                    self._spinner_thread.join(timeout=0.2)

    def solve(self, target: Optional[str] = None, verbose: bool = False) -> int:
        """
        Solve a Wordle puzzle optimally.

        Args:
            target: The target word (if None, randomly selected)
            verbose: If True, print each guess and feedback

        Returns:
            Number of guesses taken
        """
        if target is None:
            import random

            target = random.choice(self.la_words).upper()
        else:
            target = target.upper()

        possible_words = set(self.la_words)
        valid_guesses = set(self.all_words)
        guesses = []

        while True:
            guess = self._choose_optimal_guess(possible_words, valid_guesses)
            guesses.append(guess)
            feedback = self._get_feedback(guess, target)

            if verbose:
                feedback_str = "".join(
                    [
                        (
                            "🟩"
                            if c == Color.GREEN
                            else "🟨" if c == Color.YELLOW else "⬛"
                        )
                        for _, c in feedback
                    ]
                )
                print(f"Guess {len(guesses)}: {guess} {feedback_str}")

            if guess == target:
                return len(guesses)

            possible_words = self._filter_words(possible_words, guess, feedback)

            if not possible_words:
                if verbose:
                    print(f"Error: No possible words remaining after guess {guess}")
                return len(guesses)

    def play_game(self, target: Optional[str] = None) -> Tuple[int, bool]:
        """
        Play a game using the WordleGame class.

        Args:
            target: The target word (if None, randomly selected)

        Returns:
            Tuple of (number of guesses, whether won)
        """
        if target is None:
            import random

            target = random.choice(self.la_words).upper()

        game = WordleGame()
        game.target = target.upper()
        possible_words = set(self.la_words)
        valid_guesses = set(game.valid_guesses)

        while not game.is_game_over():
            guess = self._choose_optimal_guess(possible_words, valid_guesses)

            if not game.make_guess(guess):
                print(f"Error: Invalid guess {guess}")
                break

            feedback = game.all_guesses[-1]

            if game.is_won():
                return (game.attempts, True)

            possible_words = self._filter_words(possible_words, guess, feedback)

            if not possible_words:
                break

        return (game.attempts, game.is_won())

    def solve_from_state(
        self, previous_guesses: List[Tuple[str, str]], verbose: bool = True
    ) -> int:
        """
        Solve a Wordle puzzle starting from a given state with previous guesses.

        Args:
            previous_guesses: List of (guess, feedback) tuples where feedback is
                             a 5-character string of G/Y/X (green/yellow/gray)
            verbose: If True, print each guess and additional info

        Returns:
            Number of guesses taken (including previous guesses)
        """
        possible_words = set(self.la_words)
        valid_guesses = set(self.all_words)
        guesses = []

        print("Continuing from previous guesses...\n")

        for guess, feedback_str in previous_guesses:
            guess = guess.upper()
            if len(feedback_str) != 5 or not all(
                c in "GYX" for c in feedback_str.upper()
            ):
                print(f"Invalid feedback format: {feedback_str}")
                continue

            guesses.append(guess)

            feedback = []
            for i, char in enumerate(feedback_str.upper()):
                if char == "G":
                    feedback.append((guess[i], Color.GREEN))
                elif char == "Y":
                    feedback.append((guess[i], Color.YELLOW))
                else:
                    feedback.append((guess[i], Color.GRAY))

            if verbose:
                print(f"Previous guess {len(guesses)}: {guess} {feedback_str.upper()}")

            if all(c == Color.GREEN for _, c in feedback):
                print(f"\nAlready solved in {len(guesses)} guesses!")
                return len(guesses)

            possible_words = self._filter_words(possible_words, guess, feedback)

            if not possible_words:
                print(f"Error: No possible words remaining after guess {guess}")
                return len(guesses)

            if verbose:
                print(f"Remaining possibilities: {len(possible_words)}")
                if len(possible_words) <= 10:
                    print(f"Possible words: {', '.join(sorted(possible_words))}")
                print()

        print("Continuing to solve...\n")

        while True:
            guess = self._choose_optimal_guess(possible_words, valid_guesses)
            guesses.append(guess)

            print(f"Guess {len(guesses)}: {guess}")

            while True:
                feedback_input = input("Feedback (G/Y/X): ").strip().upper()
                if len(feedback_input) == 5 and all(c in "GYX" for c in feedback_input):
                    break
                print(
                    "Invalid input. Enter 5 characters: G (green), Y (yellow), X (gray)"
                )

            feedback = []
            for i, char in enumerate(feedback_input):
                if char == "G":
                    feedback.append((guess[i], Color.GREEN))
                elif char == "Y":
                    feedback.append((guess[i], Color.YELLOW))
                else:
                    feedback.append((guess[i], Color.GRAY))

            if all(c == Color.GREEN for _, c in feedback):
                print(f"\nSolved in {len(guesses)} guesses!")
                return len(guesses)

            possible_words = self._filter_words(possible_words, guess, feedback)

            if not possible_words:
                print(f"Error: No possible words remaining after guess {guess}")
                return len(guesses)

            if verbose:
                print(f"Remaining possibilities: {len(possible_words)}")
                if len(possible_words) <= 10:
                    print(f"Possible words: {', '.join(sorted(possible_words))}")
            print()

    def solve_interactive(self, verbose: bool = True) -> int:
        """
        Solve a Wordle puzzle interactively by getting feedback from user.

        Args:
            verbose: If True, print each guess and additional info

        Returns:
            Number of guesses taken
        """
        possible_words = set(self.la_words)
        valid_guesses = set(self.all_words)
        guesses = []

        print("Interactive Wordle Solver")
        print("Enter feedback as 5 characters: G (green), Y (yellow), X (gray)")
        print("Example: GYXXG means first letter green, second yellow, rest gray\n")

        while True:
            guess = self._choose_optimal_guess(possible_words, valid_guesses)
            guesses.append(guess)

            print(f"Guess {len(guesses)}: {guess}")

            while True:
                feedback_input = input("Feedback (G/Y/X): ").strip().upper()
                if len(feedback_input) == 5 and all(c in "GYX" for c in feedback_input):
                    break
                print(
                    "Invalid input. Enter 5 characters: G (green), Y (yellow), X (gray)"
                )

            feedback = []
            for i, char in enumerate(feedback_input):
                if char == "G":
                    feedback.append((guess[i], Color.GREEN))
                elif char == "Y":
                    feedback.append((guess[i], Color.YELLOW))
                else:
                    feedback.append((guess[i], Color.GRAY))

            if all(c == Color.GREEN for _, c in feedback):
                print(f"\nSolved in {len(guesses)} guesses!")
                return len(guesses)

            possible_words = self._filter_words(possible_words, guess, feedback)

            if not possible_words:
                print(f"Error: No possible words remaining after guess {guess}")
                return len(guesses)

            if verbose:
                print(f"Remaining possibilities: {len(possible_words)}")
                if len(possible_words) <= 10:
                    print(f"Possible words: {', '.join(sorted(possible_words))}")
            print()

    def solve_with_game(self, game: WordleGame, verbose: bool = True) -> int:
        """
        Solve a Wordle puzzle using a WordleGame instance.

        Args:
            game: WordleGame instance to play
            verbose: If True, print each guess and feedback

        Returns:
            Number of guesses taken
        """
        possible_words = set(self.la_words)
        valid_guesses = set(game.valid_guesses)
        guesses = []

        while not game.is_game_over():
            guess = self._choose_optimal_guess(possible_words, valid_guesses)
            guesses.append(guess)

            if not game.make_guess(guess):
                if verbose:
                    print(f"Error: Invalid guess {guess}")
                break

            feedback = game.all_guesses[-1]

            if verbose:
                feedback_str = "".join(
                    [
                        ("G" if c == Color.GREEN else "Y" if c == Color.YELLOW else "X")
                        for _, c in feedback
                    ]
                )
                print(f"Guess {len(guesses)}: {guess} {feedback_str}")

            if game.is_won():
                if verbose:
                    print(f"\nSolved in {len(guesses)} guesses!")
                return len(guesses)

            possible_words = self._filter_words(possible_words, guess, feedback)

            if not possible_words:
                if verbose:
                    print(f"Error: No possible words remaining after guess {guess}")
                break

            if verbose and len(possible_words) <= 10:
                print(f"Remaining: {len(possible_words)} words")

        return len(guesses)


def main():
    """Main entry point for the bot."""
    import argparse

    parser = argparse.ArgumentParser(description="Optimal Wordle Bot")
    parser.add_argument(
        "--target",
        type=str,
        help="Target word to solve (default: random)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="Number of games to play (default: 1)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics over multiple games",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode: solve a word by entering feedback manually",
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="Play against a WordleGame instance (bot doesn't know the answer)",
    )
    parser.add_argument(
        "--state",
        type=str,
        help="Continue from previous guesses. Format: 'GUESS1:FEEDBACK1,GUESS2:FEEDBACK2' (e.g., 'ROATE:XYGXY,CRANE:GGGXX')",
    )
    args = parser.parse_args()

    bot = WordleBot()

    if args.state:
        try:
            previous_guesses = []
            for item in args.state.split(","):
                if ":" not in item:
                    print(f"Invalid format: {item}. Use 'GUESS:FEEDBACK' format.")
                    sys.exit(1)
                guess, feedback = item.split(":", 1)
                previous_guesses.append((guess.strip(), feedback.strip()))
            bot.solve_from_state(previous_guesses, verbose=True)
        except Exception as e:
            print(f"Error parsing state: {e}")
            sys.exit(1)
    elif args.interactive:
        bot.solve_interactive(verbose=True)
    elif args.play:
        game = WordleGame()
        guesses = bot.solve_with_game(game, verbose=True)
        print(f"\nTarget was: {game.target}")
        print(f"Solved in {guesses} guesses!")
    elif args.stats or args.games > 1:
        results = []
        for i in range(args.games):
            guesses = bot.solve(verbose=args.verbose)
            results.append(guesses)
            if args.verbose:
                print(f"Game {i + 1}: {guesses} guesses\n")

        if args.stats:
            print(f"\nStatistics over {args.games} games:")
            print(f"Average guesses: {sum(results) / len(results):.2f}")
            print(f"Min guesses: {min(results)}")
            print(f"Max guesses: {max(results)}")
            print(f"Distribution: {dict(Counter(results))}")
    else:
        guesses = bot.solve(target=args.target, verbose=True)
        print(f"\nSolved in {guesses} guesses!")


if __name__ == "__main__":
    main()
