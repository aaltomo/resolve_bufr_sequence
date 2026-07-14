# CLAUDE.md - Resolve BUFR Sequence Project Guide

This project uses Python. Always assume Python conventions, type hints, and Python tooling (pytest, ruff/flake8, ty) unless otherwise specified.

## Code Review & Analysis section at the top level of CLAUDE.md\n\n

When performing project analysis or code review, break the response into numbered sections and deliver the most critical findings first. If the analysis is lengthy, summarize key points upfront before diving into details.

## Build & Test Commands

- Run all tests: `pytest`
- Run single test: `pytest tests/test_all.py::test_read -v`
- Type checking: `ty check src/`
- Linting: `ruff check src/`
- Fix linting issues: `ruff check --fix src/`

## Code Style Guidelines

- Line length: 120 characters max
- Strict type checking with mypy
- Use absolute imports
- Error handling: Use try/except with explicit error types
- Naming: snake_case for functions/variables, PascalCase for classes
- String formatting: f-strings preferred
- Imports: group standard library, then third-party, then project imports
- Functions should have return type annotations
- Use pathlib for file operations, not os.path
- Add docstrings to all functions, methods, and classes

Add under a new ## Code Review & Analysis section at the top level of CLAUDE.md\n\nWhen performing project analysis or code review, break the response into numbered sections and deliver the most critical findings first. If the analysis is lengthy, summarize key points upfront before diving into details.
