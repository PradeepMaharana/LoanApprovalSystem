# Contributing to LoanApprovalSystem

Thank you for considering contributing to the LoanApprovalSystem! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/PradeepMaharana/LoanApprovalSystem.git
   cd LoanApprovalSystem
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_security.py -v

# Run with markers
pytest -m unit
pytest -m integration
```

### Code Style

This project follows PEP 8 and uses:

- **Black** for code formatting
- **Pylint** for linting
- **MyPy** for type checking
- **Isort** for import sorting

**Format code before submitting:**
```bash
black src tests
isort src tests
pylint src
mypy src
```

## Development Workflow

### 1. Create a Branch

Use descriptive branch names following this pattern:
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring
- `test/description` - Test additions

```bash
git checkout -b feature/add-authentication
```

### 2. Make Changes

- Write clean, readable code
- Add type hints for all functions
- Include docstrings for classes and functions
- Add comprehensive tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest

# Check test coverage
pytest --cov=src

# Code quality checks
black --check src
pylint src
mypy src
```

**Coverage Requirements:**
- Minimum 70% overall coverage
- 100% for new critical code
- 90%+ for new features

### 4. Commit Changes

Use clear, descriptive commit messages:

```
feat: Add JWT authentication

- Implement token generation and validation
- Add role-based access control
- Add audit logging for sensitive operations

Closes #123
```

**Commit message format:**
```
<type>: <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 5. Submit a Pull Request

1. Push your branch to the repository
2. Open a PR with a clear description
3. Link related issues with `Closes #issue-number`
4. Ensure CI/CD checks pass
5. Request review from maintainers

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Coverage ≥ 70%
```

## Reporting Issues

Before creating an issue:
- Check existing issues and discussions
- Ensure your environment meets requirements
- Test with the latest version

**When reporting:**
- Use clear title
- Provide detailed reproduction steps
- Include environment details
- Attach relevant logs/screenshots

## Pull Request Process

1. Update README.md with any new features/changes
2. Update documentation files
3. Ensure all tests pass (pytest with coverage)
4. Ensure code follows style guide (black, pylint, mypy)
5. Get approval from at least one maintainer
6. Squash commits if requested
7. Merge when approved

## Code Review Guidelines

When reviewing code:
- Check for correctness and quality
- Verify tests are comprehensive
- Ensure documentation is clear
- Look for security issues
- Provide constructive feedback

## Development Best Practices

### Security
- Never commit secrets or credentials
- Use `.env.example` for environment templates
- Validate all user inputs
- Log sensitive operations for audit trail

### Performance
- Consider database query efficiency
- Use caching appropriately
- Monitor response times
- Profile before and after optimization

### Testing
- Write tests for new features
- Test edge cases
- Include integration tests
- Mock external dependencies

### Documentation
- Add docstrings to all functions
- Update README for new features
- Include usage examples
- Document breaking changes

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality
- PATCH: Backward-compatible bug fixes

### Release Steps
1. Update version in package metadata
2. Update CHANGELOG.md
3. Create release tag
4. Build and push Docker image
5. Publish release notes

## Getting Help

- **Questions**: Open a discussion
- **Bugs**: Create an issue
- **Ideas**: Start a discussion
- **Security**: Email security@example.com

## Additional Resources

- [Architecture Documentation](AGENT_ORCHESTRATOR_GUIDE.md)
- [API Documentation](src/api/)
- [Testing Guide](tests/)
- [Deployment Guide](deployment/)

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing! 🎉
