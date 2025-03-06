# Fabulous CLI (fabulous-cli)

A basic Python command-line interface example without external dependencies.

## Installation

```bash
# Install from PyPI
pip install fabulous-cli

# Install locally for development
pip install -e .
```

## Usage

Once installed, you can use the `fab` command:

```bash
# Default usage
fab

# Custom message
fab "This is fabulous!"

# Show version
fab --version
```

## Manual Publishing to PyPI

To publish this package to PyPI, follow these steps:

### 1. Prepare your environment

```bash
# Install build tools
pip install --upgrade pip
pip install --upgrade build twine
```

### 2. Build the package

```bash
# Build the package
python -m build
```

This will create distribution packages in the `dist/` directory.

### 3. Upload to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You will be prompted for your PyPI username and password.

### 4. Upload to TestPyPI (optional)

To test your package before uploading to the main PyPI repository:

```bash
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Then install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ fabulous-cli
```

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/yourusername/fabulous-cli.git
cd fabulous-cli

# Install in development mode
pip install -e .
```