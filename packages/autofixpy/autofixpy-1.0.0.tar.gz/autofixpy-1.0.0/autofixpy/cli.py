import argparse
import os
from autofixpy.core import scan_code, fix_code

def main():
    parser = argparse.ArgumentParser(description="AutoFixPy - Automatically fix Python errors.")
    parser.add_argument("--scan", help="Scan a Python file for issues.", type=str)
    parser.add_argument("--fix", help="Fix issues in a Python file.", type=str)

    args = parser.parse_args()

    if args.scan:
        if not os.path.exists(args.scan):
            print("Error: File not found!")
            return
        with open(args.scan, "r") as f:
            code = f.read()
        issues = scan_code(code)
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("No issues found!")

    if args.fix:
        if not os.path.exists(args.fix):
            print("Error: File not found!")
            return
        with open(args.fix, "r") as f:
            code = f.read()
        fixed_code = fix_code(code)
        with open(args.fix, "w") as f:
            f.write(fixed_code)
        print("Issues fixed!")

if __name__ == "__main__":
    main()
