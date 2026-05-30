#!/usr/bin/env python3
import random
import sys
import os

# ANSI color codes
GREEN  = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GRAY   = "\033[100m\033[97m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

WORD_LIST = [
    "apple", "brave", "chair", "dance", "eagle", "fable", "grace", "haste",
    "inlet", "joker", "kneel", "lance", "maple", "niece", "octet", "piano",
    "queen", "river", "stone", "tiger", "umbra", "viola", "waltz", "xenon",
    "yacht", "zebra", "blaze", "crisp", "drape", "ember", "flank", "gloom",
    "hinge", "irony", "jarry", "knack", "lemon", "mirth", "nerve", "optic",
    "pinch", "quirk", "ranch", "scone", "trout", "ulcer", "vapor", "whisk",
    "yearn", "zonal", "algae", "brine", "crave", "dwarf", "easel", "frown",
    "grind", "haven", "icing", "joust", "karma", "leech", "mourn", "notch",
    "olive", "perch", "quota", "revel", "shawl", "thorn", "unwed", "vivid",
    "wrath", "expel", "young", "zesty", "album", "bland", "coral", "depot",
    "epoch", "finch", "guava", "heron", "ionic", "jumpy", "kayak", "libel",
    "maxim", "nymph", "orbit", "proxy", "quirp", "resin", "skimp", "toxic",
    "unify", "verge", "worry", "xylem", "yodel", "zilch", "abyss", "broth",
    "crumb", "daunt", "evoke", "flair", "graft", "hazel", "imply", "julep",
    "knave", "lusty", "mayhem", "nobly", "onset", "plumb", "quaff", "rivet",
    "snare", "twirl", "usurp", "vouch", "whelp", "exact", "zappy", "abide",
    "boxer", "caulk", "delve", "ethos", "flute", "gruel", "hyena", "inept",
    "jowls", "kapow", "lyric", "midst", "nasal", "offal", "polyp", "qualm",
    "rebut", "slump", "tapir", "undue", "viper", "woken", "expat", "yucca",
]

WORD_LIST = [w for w in WORD_LIST if len(w) == 5]

MAX_GUESSES = 6
STATS_FILE = os.path.join(os.path.dirname(__file__), ".wordle_stats")


def load_stats():
    stats = {"streak": 0, "best_streak": 0, "played": 0, "won": 0}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE) as f:
                for line in f:
                    k, v = line.strip().split("=")
                    stats[k] = int(v)
        except Exception:
            pass
    return stats


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        for k, v in stats.items():
            f.write(f"{k}={v}\n")


def color_guess(guess, target):
    result = []
    target_chars = list(target)
    colored = [""] * 5

    # First pass: greens
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            colored[i] = GREEN + f" {g.upper()} " + RESET
            target_chars[i] = None

    # Second pass: yellows and grays
    for i, g in enumerate(guess):
        if colored[i]:
            continue
        if g in target_chars:
            colored[i] = YELLOW + f" {g.upper()} " + RESET
            target_chars[target_chars.index(g)] = None
        else:
            colored[i] = GRAY + f" {g.upper()} " + RESET

    return "".join(colored)


def print_header():
    print()
    print(BOLD + "  ╔══════════════════════╗" + RESET)
    print(BOLD + "  ║    W O R D L E  🟩   ║" + RESET)
    print(BOLD + "  ╚══════════════════════╝" + RESET)
    print()


def print_stats(stats):
    streak_bar = "🔥 " * min(stats["streak"], 5) if stats["streak"] else ""
    pct = round(100 * stats["won"] / stats["played"]) if stats["played"] else 0
    print(DIM + f"  Played: {stats['played']}  Won: {pct}%  "
          f"Streak: {stats['streak']}  Best: {stats['best_streak']}  {streak_bar}" + RESET)
    print()


def print_keyboard(used_letters):
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    print()
    for row in rows:
        print("  ", end="")
        for ch in row:
            status = used_letters.get(ch, "unused")
            if status == "green":
                print(GREEN + f" {ch.upper()} " + RESET, end="")
            elif status == "yellow":
                print(YELLOW + f" {ch.upper()} " + RESET, end="")
            elif status == "gray":
                print(GRAY + f" {ch.upper()} " + RESET, end="")
            else:
                print(f" {ch.upper()} ", end="")
        print()
    print()


def update_keyboard(used_letters, guess, target):
    priority = {"green": 3, "yellow": 2, "gray": 1, "unused": 0}
    target_chars = list(target)
    result = {}

    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            result[g] = "green"
            target_chars[i] = None

    for i, g in enumerate(guess):
        if g in result and result[g] == "green":
            continue
        if g in target_chars:
            result[g] = "yellow"
            target_chars[target_chars.index(g)] = None
        else:
            result.setdefault(g, "gray")

    for ch, status in result.items():
        if priority[status] > priority.get(used_letters.get(ch, "unused"), 0):
            used_letters[ch] = status


def play_game(stats):
    target = random.choice(WORD_LIST)
    guesses = []
    used_letters = {}

    print_header()
    print_stats(stats)
    print(DIM + "  Guess the 5-letter word in 6 tries." + RESET)
    print(DIM + "  🟩 = right spot  🟨 = wrong spot  ⬛ = not in word" + RESET)
    print()

    for attempt in range(1, MAX_GUESSES + 1):
        # Print previous guesses
        os.system("clear")
        print_header()
        print_stats(stats)

        for row_idx, g in enumerate(guesses):
            print(f"  {row_idx + 1}. {color_guess(g, target)}")
        # Empty rows
        for i in range(len(guesses), MAX_GUESSES):
            print(f"  {i + 1}. " + "".join([GRAY + "   " + RESET for _ in range(5)]))

        print_keyboard(used_letters)
        print(f"  Guess {attempt}/{MAX_GUESSES}: ", end="", flush=True)

        try:
            guess = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Thanks for playing!\n")
            sys.exit(0)

        if len(guess) != 5 or not guess.isalpha():
            print(f"  ⚠️  Please enter a valid 5-letter word.")
            input("  Press Enter to continue...")
            continue

        guesses.append(guess)
        update_keyboard(used_letters, guess, target)

        if guess == target:
            os.system("clear")
            print_header()
            print_stats(stats)
            for row_idx, g in enumerate(guesses):
                print(f"  {row_idx + 1}. {color_guess(g, target)}")
            print_keyboard(used_letters)
            msgs = ["Genius! 🧠", "Magnificent! ✨", "Impressive! 💪",
                    "Splendid! 🌟", "Great! 👍", "Phew! 😅"]
            print(f"\n  {msgs[attempt - 1]}  You got it in {attempt}!\n")
            return True

    os.system("clear")
    print_header()
    print_stats(stats)
    for row_idx, g in enumerate(guesses):
        print(f"  {row_idx + 1}. {color_guess(g, target)}")
    print_keyboard(used_letters)
    print(f"\n  The word was: {BOLD}{target.upper()}{RESET}\n")
    return False


def main():
    stats = load_stats()

    while True:
        won = play_game(stats)
        stats["played"] += 1
        if won:
            stats["won"] += 1
            stats["streak"] += 1
            stats["best_streak"] = max(stats["streak"], stats["best_streak"])
        else:
            stats["streak"] = 0
        save_stats(stats)

        print("  Play again? (y/n): ", end="", flush=True)
        try:
            again = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            again = "n"

        if again != "y":
            print(f"\n  Final stats — Played: {stats['played']}  "
                  f"Won: {stats['won']}  Best streak: {stats['best_streak']}\n")
            break


if __name__ == "__main__":
    main()
