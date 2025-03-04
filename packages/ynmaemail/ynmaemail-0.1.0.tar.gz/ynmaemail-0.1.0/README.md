# My Package

A simple Python package example.

## Installation

```bash
pip install my-package
```

## Usage

```python
from my_package import MyClass

obj = MyClass("World")
print(obj.greet())  # Output: Hello, World!

# Process some data
result = obj.process_data([1, 2, 3])
print(result)  # Output: [2, 4, 6]
```

## Development

1. Clone the repository
2. Install development dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m unittest discover tests`