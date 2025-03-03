# InternalTokenService - Python Package

## Overview

The `InternalTokenService` is a Python package that helps with generating and validating JWT tokens. It leverages the HMAC-SHA256 algorithm for securing tokens and includes features for expiration, payload management, and traceability via request IDs.

This package is suitable for use in microservices, secure API communications, or any scenario where short-lived tokens need to be generated, validated, and tracked.

## Features

- **JWT Token Generation:** Securely generate JWT tokens from Python objects or dictionaries.
- **Token Validation:** Validate JWT tokens to ensure their authenticity and integrity.
- **Traceability:** Automatically generate unique request IDs for tracing requests.
- **Expiration Handling:** Easily handle token expiration with customizable expiration times.

## Installation

You can install the package using `pip` from the source directory:

```bash
pip install .
```

## Usage

### 1. Importing the Class

Import the `InternalTokenService` class into your Python project:

```python
from internal_token_service import InternalTokenService
```

### 2. Generating a Token

There are two methods to generate a JWT token:

- **Using a custom Python object** (e.g., user data class).
- **Using a dictionary** (if you already have your payload as a dictionary).

#### Example with Custom Python Object:

```python
class UserPayload:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

# Initialize payload data
payload = UserPayload(user_id=1, username="john_doe")
secret_key = "my_secret_key"
expiration_time = 3600  # Token expires in 1 hour

# Generate the token
token = InternalTokenService.generate_internal_token(secret_key, expiration_time, payload)
print("Generated Token:", token)
```

#### Example with Dictionary Payload:

```python
payload = {
    "user_id": 1,
    "username": "john_doe"
}
secret_key = "my_secret_key"
expiration_time = 3600  # Token expires in 1 hour

# Generate the token
token = InternalTokenService.generate_internal_token_for_dict(secret_key, expiration_time, payload)
print("Generated Token:", token)
```

### 3. Validating a Token

To validate a JWT token, use the `validate_token` method:

```python
try:
    decoded_data = InternalTokenService.validate_token(secret_key, token)
    print("Decoded Token:", decoded_data)
except ValueError as e:
    print("Error:", e)
```

### 4. Generating a Request ID

The `generate_trace_id` method generates a unique request ID:

```python
request_id = InternalTokenService.generate_trace_id()
print("Generated Request ID:", request_id)
```

## Methods

### `InternalTokenService.generate_internal_token(secret, expiration_time_in_seconds, payload_obj)`

Generates a JWT token with a payload object.

- **secret**: Secret key for signing the token.
- **expiration_time_in_seconds**: Expiration time in seconds.
- **payload_obj**: A Python object containing the data to be encoded.

Returns an encoded JWT token as a string.

### `InternalTokenService.generate_internal_token_for_dict(secret, expiration_time_in_seconds, payload)`

Generates a JWT token with a dictionary payload.

- **secret**: Secret key for signing the token.
- **expiration_time_in_seconds**: Expiration time in seconds.
- **payload**: Dictionary containing the data to be encoded.

Returns an encoded JWT token as a string.

### `InternalTokenService.validate_token(secret, token)`

Validates a JWT token and decodes its payload.

- **secret**: Secret key used for signing the token.
- **token**: JWT token to decode and validate.

Returns the decoded payload as a dictionary or raises `ValueError` if invalid.

### `InternalTokenService.generate_trace_id()`

Generates a unique request ID for tracing.

Returns a string representing the generated UUID.

## Error Handling

- **Token Expiry:** Raises `ValueError("Token has expired")` if the token is expired.
- **Invalid Token:** Raises `ValueError("Invalid token")` if the token is invalid.
- **Other Errors:** Raises `ValueError` with an appropriate message for any other error.

## Dependencies

This package requires:

- `PyJWT` for handling JWT encoding and decoding:
  ```bash
  pip install pyjwt
  ```
- `uuid` and `datetime` (part of Python's standard library).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

