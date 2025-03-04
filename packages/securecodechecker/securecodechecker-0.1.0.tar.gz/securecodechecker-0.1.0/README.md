# SecureCodeChecker

SecureCodeChecker is a Python module designed to help you identify common insecure coding patterns in your Python code. It is intended for educational and ethical research purposes only—always use such tools legally and responsibly.

## Features

- Scans Python code (as a string or from a file) for potential security issues.
- Detects use of dangerous functions like `eval()`, `exec()`, insecure use of `os.system()`, and more.
- Provides suggestions for safer coding practices.

## Installation

### Via PyPI (once published)
```bash
pip install securecodechecker



git clone https://github.com/yourusername/securecodechecker.git
cd securecodechecker
pip install .
