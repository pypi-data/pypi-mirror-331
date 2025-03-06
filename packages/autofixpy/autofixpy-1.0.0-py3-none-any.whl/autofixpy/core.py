import re

def scan_code(code):
    """Scans code for common Python issues."""
    issues = []
    if "==" in code and "if" not in code:  # Example issue
        issues.append("Possible missing 'if' statement before '==' comparison.")
    return issues

def fix_code(code):
    """Attempts to automatically fix common issues."""
    code = re.sub(r"print (.+)", r"print(\1)", code)  # Fix missing parentheses in print
    return code
