# Leja Recharge Python SDK

[![Python Package CI/CD](https://github.com/Asilimia/leja-recharge-python-sdk/actions/workflows/workflow.yml/badge.svg)](https://github.com/Asilimia/leja-recharge-python-sdk/actions/workflows/workflow.yml)

A Python SDK for interacting with the Leja Recharge API.

## Documentation
Take a look at the [API docs here](https://recharge.leja.co.ke/redoc)

## Installation

```bash
pip install leja-recharge-sdk
```

## Authentication

The SDK uses Basic Authentication with your Client ID and API key (Both found on the your dashboard). You'll need both credentials to initialize the client:

```python
from leja_recharge_sdk import LejaRechargeClient

# Initialize the client with your credentials
client = LejaRechargeClient(
    client_id="your_client_id",
    api_key="your_api_key"
)
```

## Quick Start

```python
from leja_recharge_sdk import LejaRechargeClient, AirtimeRecipient

# Initialize the client with your credentials
client = LejaRechargeClient(
    client_id="your_client_id",
    api_key="your_api_key"
)

# Purchase airtime
recipients = [
    AirtimeRecipient(
        phone_number="+254712345678",
        amount=10.0,
        country="KE"
    )
]

transaction = client.purchase_airtime(
    phone_number="+254712345678",
    recipients=recipients,
    is_async=True,
    callback_url="https://your-callback-url.com/webhook"
)

# Get transaction details
transaction_details = client.get_transaction(tracking_id=transaction.tracking_id)

# Get account balance
balance = client.get_balance()

# Get supported countries
countries = client.get_countries(page=1, limit=20)
```

## Features

- Purchase airtime for multiple recipients
- Get transaction details
- Check account balance
- List supported countries
- Async support for airtime purchases
- Webhook callbacks for async transactions
- Comprehensive error handling
- Type hints for better IDE support
- Pagination support for listing endpoints

## Error Handling

The SDK provides custom exceptions for different error scenarios:

```python
from leja_recharge.exceptions import (
    LejaRechargeError,
    AuthenticationError,
    ValidationError,
    APIError,
    NetworkError
)

try:
    client = LejaRechargeClient(
        client_id="invalid_client_id",
        api_key="invalid_api_key"
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Exception Types

- `LejaRechargeError`: Base exception class for all SDK errors
- `AuthenticationError`: Raised when authentication fails
- `ValidationError`: Raised when input validation fails
- `APIError`: Raised when the API returns an error response
- `NetworkError`: Raised when network communication fails

## Models

The SDK provides type-safe models for all API responses:

- `AirtimeRecipient`: Model for airtime purchase recipients
- `Transaction`: Model for transaction details
- `Balance`: Model for account balance
- `Country`: Model for supported country information
- `PaginatedResponse`: Generic model for paginated responses

## Development

1. Clone the repository
   ```bash
   git clone https://github.com/Asilimia/leja-recharge-py-sdk.git
   cd leja-recharge-py-sdk
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run tests:
   ```bash
   # Run all tests
   poetry run pytest

   # Run tests with coverage report
   poetry run pytest --cov=leja_recharge_sdk

   # Run tests verbosely
   poetry run pytest -v
   ```

### Testing

The test suite includes:

- Unit tests for all SDK functionality
- Mock tests for API interactions
- Model validation tests
- Error handling tests
- Integration test examples

Test files are organized as follows:
- `tests/conftest.py`: Shared pytest fixtures
- `tests/test_client.py`: Client functionality tests
- `tests/test_models.py`: Data model tests
- `tests/test_exceptions.py`: Exception handling tests

## Publishing

To publish a new version of the package:

1. Update version numbers in relevant files:
   ```bash
   # Update version in pyproject.toml or setup.py
   # Update version in __init__.py if applicable
   # Update CHANGELOG.md with your changes
   ```

2. Run tests to ensure everything is working:
   ```bash
   poetry run pytest
   ```

3. Create and push a new Git tag:
   ```bash
   # Create a new tag
   git tag -a v1.0.0 -m "Version 1.0.0"
   
   # Push the tag
   git push origin v1.0.0
   ```

4. The GitHub Actions workflow will automatically:
   - Run tests across Python versions 3.8-3.11
   - Build the package
   - Publish to PyPI if all tests pass

Note: Make sure you have:
- Updated all version numbers consistently
- Added all changes to CHANGELOG.md
- Committed all changes to main branch
- Have proper PyPI credentials configured in GitHub Secrets

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License 