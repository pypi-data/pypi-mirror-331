# MathUtils

A simple Python package providing basic mathematical utilities.

## Features

- **Arithmetic Operations**: Basic functions like add, subtract, multiply, and divide
- **Statistical Functions**: Calculate mean, median, mode, and standard deviation
- **Vector Operations**: Perform dot product, cross product, and calculate vector magnitude

## Installation

You can install the package from PyPI:

```bash
pip install arunmoorthy-mathutils
```

Or install directly from the repository:

```bash
git clone https://github.com/yourusername/mathutils.git
cd mathutils
pip install -e .
```

## Quick Start

```python
import mathutils

# Arithmetic
result = mathutils.add(5, 3)  # 8

# Statistics
data = [1, 2, 3, 4, 5]
avg = mathutils.mean(data)  # 3.0

# Vectors
v1 = [1, 2, 3]
v2 = [4, 5, 6]
dot = mathutils.dot_product(v1, v2)  # 32
```

For more examples, check the `examples` directory.

## Documentation

For detailed documentation, see the `docs` directory or visit our [documentation site](https://example.com/mathutils-docs).

## Development

### Prerequisites

- Python 3.7 or higher

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/yourusername/mathutils.git
cd mathutils

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 