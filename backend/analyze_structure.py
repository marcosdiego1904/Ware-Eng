"""
Analyze the structure around the problematic method more thoroughly
"""

def analyze_structure():
    with open('src/rule_engine.py', 'r') as f:
        lines = f.readlines()

    print("Analyzing structure around _assign_location_types_with_context")
    print("=" * 60)

    # Find the target method
    target_line = None
    for i, line in enumerate(lines):
        if '_assign_location_types_with_context' in line and 'def ' in line:
            target_line = i
            break

    if target_line is None:
        print("Method not found!")
        return

    # Show detailed context
    start = max(0, target_line - 20)
    end = min(len(lines), target_line + 30)

    for i in range(start, end):
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        marker = ""
        if i == target_line:
            marker = " <-- TARGET METHOD"
        elif 'def ' in stripped and stripped.startswith('def '):
            marker = " <-- METHOD"
        elif 'class ' in stripped and stripped.startswith('class '):
            marker = " <-- CLASS"

        # Highlight important lines
        if marker or indent <= 4:
            print(f"{i+1:4d}: [{indent:2d}] {repr(line.rstrip())}{marker}")

    # Look for the previous method end
    print("\nLooking for previous method's end:")
    for i in range(target_line - 1, max(0, target_line - 50), -1):
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if 'def ' in stripped and stripped.startswith('def '):
            print(f"Previous method starts at line {i+1}: {stripped.strip()}")
            break

        if 'return ' in stripped and indent == 8:  # Method return at class method level
            print(f"Previous method likely ends at line {i+1}: {stripped.strip()}")
            break

if __name__ == "__main__":
    analyze_structure()