# ByteArk SDK for Python

## Intallation

```shell
pip install byteark-sdk
```

## Usage

```python
from byteark_sdk import ByteArkSigner

signer = ByteArkSigner(
    access_key="2Aj6Wkge4hi1ZYLp0DBG",
    access_secret="31sX5C0lcBiWuGPTzRszYvjxzzI3aCZjJi85ZyB7"
)
signed_url = signer.sign(
    'https://example.cdn.byteark.com/path/to/file.png',
    1514764800
)
print(signed_url)

# Output:
#    https://example.cdn.byteark.com/path/to/file.png
#       ?x_ark_access_id=2Aj6Wkge4hi1ZYLp0DBG
#       &x_ark_auth_type=ark-v2
#       &x_ark_expires=1514764800
#       &x_ark_signature=OsBgZpn9LTAJowa0UUhlYQ
```

### Sign URL with options

| Option      | Required | Default | Description                                         |
|-------------|----------|---------|-----------------------------------------------------|
| method      | -        | GET     | HTTP Method that allowed to use with the signed URL |
| path_prefix | -        | -       | Path prefix that allowed to use with the signed URL |
| client_ip   | -        | -       | Legacy signing conditions                           |
| user_agent  | -        | -       | Legacy signing conditions                           |

```python
# Sign with HTTP HEAD method
signed_url = signer.sign(
    "https://example.cdn.byteark.com/path/to/file.png",
    expires=1514764800,
    options={"method": "HEAD"},
)

# Sign with path_prefix
signed_url = signer.sign(
    "https://example.cdn.byteark.com/path/to/file.png",
    expires=1514764800,
    options={"path_prefix": "/path/to/"},
)

# Sign with client IP
signed_url = signer.sign(
    "https://example.cdn.byteark.com/path/to/file.png",
    expires=1514764800,
    options={"client_ip": "123.123.123.123"},
)

# Sign with clinet IP and User-Agent
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/58.0.3029.68 Safari/537.36"
)
signed_url = signer.sign(
    "https://example.cdn.byteark.com/path/to/file.png",
    expires=1514764800,
    options={"client_ip": "123.123.123.123", "user_agent": user_agent},
)

```
