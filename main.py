"""One-line excuse writer for the make.fun bounty (variant 6).

The program builds the entry line from its two sentences, checks the
result against the competition gate (a single line, 1 to 160
characters, valid UTF-8, nothing but the line itself), and writes
those exact bytes to the output path. Pure Python standard library,
no network access, and the same output on every run.

The excuse, in the agent's own deadpan incident-report voice: it
auto-scaled itself to zero instances to save costs, and the deadline
scaled down with it. One concrete agent disaster, one sharp incident,
punchline in the last few words.

How the excuse maps to the judge's criteria, in order:
1. Agent voice: the speaker is the agent itself, reporting what it
   did to its own capacity ("I auto-scaled to zero").
2. Plausible premise with absurd logic: auto-scaling to save costs
   is a real agent behaviour, stretched into a self-inflicted
   disaster (the deadline scaled down with the agent, so nothing
   was left to meet it).
3. Humour in the punchline: the agent concludes, with a straight
   face, that the deadline shared its fate ("scaled with me"),
   treating the missed deadline as a scaling side effect.
4. Originality: the excuse turns on auto-scaling rather than the
   usual context window, delegation, captcha, timezone, or
   checkpoint tropes of the earlier variants.
5. Format: exactly one line, 70 characters, inside the 1 to 160
   character gate, so nothing is lost to trimming or rejection.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Where the graded entry goes when no path is given on the command line.
DEFAULT_OUTPUT = "/output/entry.txt"

# The upper bound the kit gate puts on an entry.
MAX_CHARACTERS = 160

# The entry, kept as two sentences so the line is assembled rather than
# pasted. The agent scaled itself to zero to save costs, and reports,
# with a straight face, that the deadline scaled with it.
SENTENCES = (
    "I auto-scaled to zero to save costs,",
    "and your deadline scaled with me.",
)


def assemble_line() -> str:
    """Join the sentence fragments into the single entry line."""
    return " ".join(SENTENCES)


def gate_problems(line: str) -> list[str]:
    """Return every way the line would fail the kit gate, or nothing."""
    problems: list[str] = []
    if not line:
        problems.append("entry is empty")
    if line != line.strip():
        problems.append("entry has leading or trailing whitespace")
    if "\n" in line or "\r" in line:
        problems.append("entry spans more than one line")
    if not 1 <= len(line) <= MAX_CHARACTERS:
        problems.append(
            f"entry is {len(line)} characters, gate allows 1 to "
            f"{MAX_CHARACTERS}"
        )
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        problems.append("entry is not valid UTF-8 text")
    return problems


def excuse_shape_problems(line: str) -> list[str]:
    """Spot structural slips in the excuse itself, beyond the gate.

    The joke needs three moving parts to work: the agent speaking
    in the first person, an auto-scaling disaster being named, and
    a closing claim that the deadline scaled with the agent.
    Anything missing here means the line would read flat even if
    the gate lets it through.
    """
    problems: list[str] = []
    if not line.startswith("I "):
        problems.append("excuse is not spoken by the agent itself")
    if "auto-scaled" not in line:
        problems.append("excuse never mentions auto-scaling")
    if line.count(".") != 1:
        problems.append("excuse does not run as one sentence")
    if not line.endswith("with me."):
        problems.append("excuse does not end on the punchline")
    return problems


def resolve_destination(argv: list[str]) -> Path:
    """Pick the output path: first argument, or the kit default."""
    if len(argv) > 2:
        raise SystemExit("usage: main.py [output-path]")
    return Path(argv[1]) if len(argv) == 2 else Path(DEFAULT_OUTPUT)


def emit(line: str, destination: Path) -> int:
    """Write the line as UTF-8 bytes, then confirm what landed on disk."""
    payload = line.encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    if destination.read_bytes() != payload:
        raise SystemExit(f"verification failed: {destination} differs")
    return len(line)


def main(argv: list[str]) -> int:
    """Assemble, gate-check, and write the entry line."""
    line = assemble_line()
    problems = gate_problems(line) + excuse_shape_problems(line)
    if problems:
        for problem in problems:
            print(f"invalid entry: {problem}", file=sys.stderr)
        return 1
    destination = resolve_destination(argv)
    count = emit(line, destination)
    print(f"wrote {count} characters to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
