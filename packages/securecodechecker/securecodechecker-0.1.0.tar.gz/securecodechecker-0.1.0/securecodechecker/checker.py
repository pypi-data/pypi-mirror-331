"""
checker.py

SecureCodeChecker scans Python code for common insecure coding patterns
and offers suggestions for improvements. This is for educational and ethical
research purposes only.
"""

import re

# Define some example insecure patterns and their suggestions.
VULNERABILITY_PATTERNS = [
    {
        "pattern": r"\beval\s*\(",
        "message": "Usage of eval() detected. Consider using safer alternatives."
    },
    {
        "pattern": r"\bexec\s*\(",
        "message": "Usage of exec() detected. Be cautious, as it can execute arbitrary code."
    },
    {
        "pattern": r"\binput\s*\(",
        "message": "Usage of input() detected. Validate and sanitize user inputs to prevent injection attacks."
    },
    {
        "pattern": r"\bos\.system\s*\(",
        "message": "Usage of os.system() detected. Consider using subprocess with proper parameterization."
    },
    {
        "pattern": r"\bsqlite3\.connect\s*\(.*\+.*\)",
        "message": "Possible SQL injection vulnerability: avoid string concatenation when building SQL queries."
    }
    # Add more patterns as needed.
]

def check_code(code: str) -> list:
    """
    Scans the provided code (as a string) for potential insecure coding patterns.

    Args:
        code (str): The Python code to analyze.

    Returns:
        list: A list of warnings (strings) for detected patterns.
    """
    warnings = []
    for vuln in VULNERABILITY_PATTERNS:
        matches = re.findall(vuln["pattern"], code)
        if matches:
            warnings.append(vuln["message"])
    return warnings

def check_file(filename: str) -> list:
    """
    Reads a Python file and scans it for potential insecure coding patterns.

    Args:
        filename (str): Path to the Python source file.

    Returns:
        list: A list of warnings (strings) for detected patterns.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return [f"Error reading file: {e}"]
    return check_code(code)

if __name__ == "__main__":
    # For testing purposes: Scan a file specified by the user
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m securecodechecker.checker <path_to_python_file>")
    else:
        warnings = check_file(sys.argv[1])
        if warnings:
            print("Warnings:")
            for warn in warnings:
                print(f" - {warn}")
        else:
            print("No insecure patterns detected.")
