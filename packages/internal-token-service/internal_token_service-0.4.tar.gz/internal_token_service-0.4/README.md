# InternalTokenService - Python Package

## Overview

The `InternalTokenService` is a Python package that helps with generating and validating JWT tokens. It leverages the HMAC-SHA256 algorithm for securing tokens and includes features for expiration, payload management, and traceability via request IDs.

This package is suitable for use in microservices, secure API communications, or any scenario where short-lived tokens need to be generated, validated, and tracked.

## Features

- **JWT Token Generation:** Securely generate JWT tokens from Python objects or dictionaries.
- **Token Validation:** Validate JWT tokens to ensure their authenticity and integrity.
- **Traceability:** Automatically generate or use provided request IDs for tracing requests.
- **Expiration Handling:** Easily handle token expiration with customizable expiration times.

## Installation

You can install the package using `pip` from the source directory:

```bash
pip install .

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

#### Example with Custom Python Object (UserPayload):

```python
from datetime import datetime

class UserPayload:
    def __init__(self, user_id, username, request_id=None):
        self.user_id = user_id
        self.username = username
        self.request_id = request_id  # Optional request ID for tracing

# Initialize payload data
payload = UserPayload(user_id=1, username="john_doe")
secret_key = "my_secret_key"
expiration_time = 3600  # Token expires in 1 hour

# Generate the token using the InternalTokenService
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

# Generate the token using the InternalTokenService for dictionaries
token = InternalTokenService.generate_internal_token_for_dict(secret_key, expiration_time, payload)
print("Generated Token:", token)
```

### 3. Validating a Token

To validate a JWT token, use the `validate_token` method. This method takes two parameters:

- `secret`: The secret key used to decode and validate the JWT.
- `token`: The JWT token to validate and decode.

#### Example:

```python
try:
    decoded_data = InternalTokenService.validate_token(secret_key, token)
    print("Decoded Token:", decoded_data)
except ValueError as e:
    print("Error:", e)
```

### 4. Generating a Request ID

The `generate_trace_id` method generates a unique request ID, which can be useful for tracing requests across systems.

```python
request_id = InternalTokenService.generate_trace_id()
print("Generated Request ID:", request_id)
```

## Example Workflow

```python
from datetime import datetime

# Define a user payload
class UserPayload:
    def __init__(self, user_id, username, request_id=None):
        self.user_id = user_id
        self.username = username
        self.request_id = request_id

# Initialize payload data
payload = UserPayload(user_id=1, username="john_doe")
secret_key = "supersecret"
expiration_time = 600  # Token expires in 10 minutes

# Generate a token
token = InternalTokenService.generate_internal_token(secret_key, expiration_time, payload)
print("Generated Token:", token)

# Validate the token
try:
    decoded_token = InternalTokenService.validate_token(secret_key, token)
    print("Decoded Token:", decoded_token)
except ValueError as e:
    print("Error:", e)
```

## Methods

### `InternalTokenService.generate_internal_token(secret, expiration_time_in_seconds, payload_obj)`

Generates a JWT token based on the provided secret key, expiration time, and payload object.

- **secret**: The secret key used for signing the token (string).
- **expiration_time_in_seconds**: The expiration time for the token, in seconds (int).
- **payload_obj**: A Python object (e.g., `UserPayload`) containing the data to be encoded.

Returns the encoded JWT token as a string.

### `InternalTokenService.generate_internal_token_for_dict(secret, expiration_time_in_seconds, payload)`

Generates a JWT token based on the provided secret key, expiration time, and dictionary payload.

- **secret**: The secret key used for signing the token (string).
- **expiration_time_in_seconds**: The expiration time for the token, in seconds (int).
- **payload**: A dictionary containing the data to be encoded.

Returns the encoded JWT token as a string.

### `InternalTokenService.validate_token(secret, token)`

Validates a JWT token and decodes its payload.

- **secret**: The secret key used for signing the token (string).
- **token**: The JWT token to decode and validate (string).

Returns the decoded payload as a dictionary or raises a `ValueError` if the token is invalid or expired.

### `InternalTokenService.generate_trace_id()`

Generates a unique request ID, typically used for tracing requests across systems.

Returns a string representing the generated UUID.

### `JwtUtil.generate_internal_token(secret, expiration_time_in_seconds, payload)`

Generates a JWT token by encoding the payload object (either as a dictionary or a Python object) with the provided secret and expiration time. This method is used internally by `InternalTokenService`.

### `JwtUtil.validate_internal_token(secret, token)`

Validates a JWT token and decodes the payload. This method is used internally by `InternalTokenService`.

## Error Handling

- **Token Expiry:** If the token is expired, a `ValueError` with the message "Token has expired" is raised.
- **Invalid Token:** If the token is invalid, a `ValueError` with the message "Invalid token" is raised.
- **Other Errors:** Any other errors during validation or token generation will raise a `ValueError` with a relevant error message.

## Dependencies

This package requires the following external dependencies:

- `PyJWT` for handling JWT encoding and decoding:
  ```bash
  pip install pyjwt
  ```

- `uuid` and `datetime` are part of Python's standard library.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This package provides an easy-to-use utility for securely generating and validating JWT tokens, with added support for traceability using unique request IDs and flexible payload handling (object or dictionary).