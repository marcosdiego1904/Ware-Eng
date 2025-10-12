"""
Check indentation structure around the problematic method
"""

def check_indentation():
    with open('src/rule_engine.py', 'r') as f:
        lines = f.readlines()

    print("Checking indentation around _assign_location_types_with_context")
    print("=" * 60)

    target_line = None
    for i, line in enumerate(lines):
        if '_assign_location_types_with_context' in line and 'def ' in line:
            target_line = i
            break

    if target_line is None:
        print("Method not found!")
        return

    # Check lines before and after
    start = max(0, target_line - 10)
    end = min(len(lines), target_line + 20)

    for i in range(start, end):
        line = lines[i]
        # Calculate indentation
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Mark the target line
        marker = " <-- TARGET" if i == target_line else ""

        # Show special lines
        if 'def ' in line or 'class ' in line or i == target_line:
            print(f"{i+1:4d}: [{indent:2d}] {line.rstrip()}{marker}")

    # Check if there are any structural issues
    print("\nChecking for structural issues:")

    # Look for unclosed parentheses, brackets, or braces before the target line
    open_count = 0
    for i in range(max(0, target_line - 50), target_line):
        line = lines[i]
        open_count += line.count('(') - line.count(')')
        open_count += line.count('[') - line.count(']')
        open_count += line.count('{') - line.count('}')

    print(f"Open brackets/parens before target line: {open_count}")

    if open_count != 0:
        print("WARNING: Unclosed brackets/parentheses detected!")

if __name__ == "__main__":
    check_indentation()