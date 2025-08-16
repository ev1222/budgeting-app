# Backend API Test Suite

A comprehensive test suite for the backend GraphQL API modules, covering schema resolvers, types, filters, and integration workflows.

## Test Structure

```
backend/testing/
├── conftest.py              # Test configuration and fixtures
├── test_schema.py           # Tests for GraphQL resolvers and mutations
├── test_types.py            # Tests for GraphQL type definitions
├── test_filters.py          # Tests for input filter classes
├── test_integration.py      # Integration tests for full API workflows
├── run_tests.py            # Test runner script
└── README.md               # This file
```

## Test Coverage

### Schema Tests (`test_schema.py`)
- **Query resolvers**: Tests for `purchases`, `trips`, and `totals` query resolvers
- **Filter handling**: Comprehensive testing of all filter combinations
- **Mutation testing**: Tests for `sync_google_sheets` mutation
- **Field name resolution**: Tests for the `get_field_name` utility function
- **Error handling**: Tests for various error conditions

### Type Tests (`test_types.py`)
- **Type creation**: Tests for GraphQL type instantiation from Pydantic models
- **Field mapping**: Verification that all model fields are exposed in GraphQL types
- **Data validation**: Tests with various data scenarios including edge cases
- **Strawberry integration**: Tests for proper Strawberry-Pydantic integration

### Filter Tests (`test_filters.py`)
- **Input validation**: Tests for all filter input classes
- **Field types**: Verification of proper GraphQL input field types
- **Edge cases**: Tests with empty lists, null values, and boundary conditions
- **Strawberry decorators**: Verification of proper input decoration

### Integration Tests (`test_integration.py`)
- **End-to-end workflows**: Complete GraphQL query/mutation execution
- **Schema introspection**: Tests for GraphQL schema metadata
- **Complex filtering**: Tests with multiple filter combinations
- **Error propagation**: Tests for proper error handling in GraphQL operations
- **Field resolution**: Verification that all fields are properly resolvable

## Running Tests

### Prerequisites

Make sure you have pytest installed:
```bash
pip install pytest pytest-cov
```

### Basic Usage

Run all tests:
```bash
cd backend/testing
python run_tests.py
```

Run specific test modules:
```bash
python run_tests.py --module schema    # Schema tests only
python run_tests.py --module types     # Type tests only
python run_tests.py --module filters   # Filter tests only
python run_tests.py --module integration  # Integration tests only
```

### Advanced Options

Run with verbose output:
```bash
python run_tests.py --verbose
```

Run with coverage report:
```bash
python run_tests.py --coverage
```

Run directly with pytest:
```bash
pytest test_schema.py -v              # Specific file
pytest test_schema.py::TestQuery -v   # Specific class
pytest -k "purchase" -v               # Tests matching pattern
```

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

- `sample_purchases`: Mock purchase data for testing
- `sample_trips`: Mock trip data for testing  
- `sample_totals`: Mock totals data for testing
- `mock_query_data`: Mock for the `query_data` database function
- `mock_sync_google_sheets`: Mock for the Google Sheets sync function

## Mocking Strategy

The tests use comprehensive mocking to isolate the API layer:

- **Database calls**: `db.database.query_data` is mocked to return test data
- **External APIs**: `sync.data_sync.sync_google_sheets_data` is mocked
- **Dependencies**: All external dependencies are properly mocked

This ensures tests are:
- Fast (no database or API calls)
- Reliable (no external dependencies)
- Focused (testing only the API layer logic)

## Test Categories

### Unit Tests
- Individual function testing
- Input validation
- Type checking
- Error handling

### Integration Tests  
- Full GraphQL operations
- Schema validation
- End-to-end workflows
- Error propagation

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on others
2. **Mocking**: External dependencies are properly mocked
3. **Coverage**: All major code paths are tested
4. **Edge cases**: Boundary conditions and error scenarios are covered
5. **Documentation**: Tests serve as documentation for API behavior

## Continuous Integration

This test suite is designed to be run in CI/CD pipelines. The `run_tests.py` script provides proper exit codes and can generate coverage reports for integration with CI tools.

Example CI usage:
```bash
cd backend/testing
python run_tests.py --coverage
```