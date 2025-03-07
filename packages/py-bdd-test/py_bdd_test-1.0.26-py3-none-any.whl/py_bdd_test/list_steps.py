import os
import re
import importlib.util
from pathlib import Path

# Behave step decorators
STEP_PATTERNS = [r"@given\((.*?)\)", r"@when\((.*?)\)", r"@then\((.*?)\)"]


def find_step_definitions(directory):
    step_definitions = []

    for file in Path(directory).rglob("*.py"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.readlines()

        for line in content:
            for pattern in STEP_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    step_definitions.append(f"{file.name}: {match.group(1)}")

    return step_definitions


def main():
    steps_dir = Path(__file__).parent / "features" / "steps"

    if not steps_dir.exists():
        print("⚠️ No 'steps' directory found!")
        return

    print("\n📌 **BDD Step Definitions Found:**\n")
    steps = find_step_definitions(steps_dir)

    if not steps:
        print("No step definitions found.")
    else:
        for step in steps:
            print(f"✅ {step}\n")


if __name__ == "__main__":
    main()
