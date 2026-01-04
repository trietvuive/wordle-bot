# Wordle Bot

Wordle is NP-hard, so let's solve it
https://arxiv.org/abs/2203.16713

Please report all bugs to /dev/null

## Installation

No external dependencies required. Uses Python 3 standard library.

## Usage

### Play Wordle

```bash
python game/wordle.py
python game/wordle.py --hard  # Hard mode
```

### Run Bot

```bash
python bot/wordle_bot.py
python bot/wordle_bot.py --target CRANE --verbose
python bot/wordle_bot.py --games 100 --stats
python bot/wordle_bot.py --interactive  # Interactive mode (manual feedback)
python bot/wordle_bot.py --play  # Solve without knowing the answer
python bot/wordle_bot.py --state "ROATE:XYGXY,CRANE:GGGXX"  # Continue from previous guesses
```

## Project Structure

- `game/` - Wordle game implementation
- `bot/` - Optimal solving bot using information theory
- `dictionary/` - Word lists (La and Ta words)

## Bot Algorithm

Uses entropy-based decision making to minimize expected remaining words per guess. Average solve time: ~3.4 guesses.

