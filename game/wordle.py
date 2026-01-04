#!/usr/bin/env python3
"""
Wordle Game Simulator - Command Line Version
A classic Wordle game where you have 6 attempts to guess a 5-letter word.
"""

import argparse
import sys
from wordle_game import WordleGame, Colors


def play_wordle(hard_mode: bool = False):
    """Main entry point to play a Wordle game."""
    game = WordleGame(hard_mode=hard_mode)
    game.play()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play Wordle on the command line")
    parser.add_argument(
        "--hard",
        action="store_true",
        help="Enable hard mode (must use all revealed green and yellow letters)",
    )
    args = parser.parse_args()

    try:
        play_wordle(hard_mode=args.hard)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GRAY}Game interrupted. Goodbye!{Colors.RESET}")
        sys.exit(0)
