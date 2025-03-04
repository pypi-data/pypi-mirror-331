# gepo - HTTP Requests from the Command Line

`gepo` is a powerful, easy-to-use command-line tool for making HTTP requests. Built for developers, testers, and API enthusiasts who need a flexible and intuitive way to interact with web services.

## Installation

```bash
pip install gepo
```

## Basic Usage

```bash
# Simple GET request
gepo GET https://api.example.com/users

# POST request with JSON data
gepo POST https://api.example.com/users --json '{"name":"John","email":"john@example.com"}'

# PUT request with form data
gepo PUT https://api.example.com/users/1 --form "name=John&active=true"
```

## Features

- Support for all common HTTP methods
- Multiple data formats (JSON, form-data, plain text, XML, etc.)
- Custom headers and query parameters
- File uploads
- Authentication (Basic, Digest, Bearer)
- Cookies support
- Proxy configuration
- Response streaming
- Save response to file
- Verbose output

## Command-Line Options

| Flag/Option | Shorthand | Description | Example |
|-------------|-----------|-------------|---------|
| `--json` | - | Send JSON data | `gepo POST url --json '{"name":"John"}'` |
| `--form` | - | Send URL-encoded form data | `gepo POST url --form "name=John"` |
| `--text` | - | Send plain text data | `gepo POST url --text "Hello World"` |
| `--html` | - | Send HTML data | `gepo POST url --html "<h1>Hello</h1>"` |
| `--xml` | - | Send XML data | `gepo POST url --xml "<user><name>John</name></user>"` |
| `--file` | - | Upload or send a file | `gepo POST url --file image.jpg` |
| `--multipart` | - | Use multipart/form-data encoding | `gepo POST url --file image.jpg --multipart` |
| `--save` | - | Save response to a file | `gepo url --save response.txt` |
| `--stream` | - | Stream the response | `gepo url --stream` |
| `--header` | `-H` | Add a custom header | `gepo url -H "X-API-Key: abc123"` |
| `--query` | `-q` | Add a query parameter | `gepo url -q "term=python"` |
| `--auth` | - | Set authentication credentials | `gepo url --auth "username:password"` |
| `--auth-type` | - | Specify auth type (basic, digest, bearer) | `gepo url --auth "token" --auth-type bearer` |
| `--cookie` | - | Set a cookie | `gepo url --cookie "session=abc123"` |
| `--proxy` | - | Use a proxy server | `gepo url --proxy http://proxy:8080` |
| `--no-verify` | - | Disable SSL verification | `gepo url --no-verify` |
| `--timeout` | - | Set request timeout (seconds) | `gepo url --timeout 60` |
| `--max-redirects` | - | Limit number of redirects to follow | `gepo url --max-redirects 2` |
| `--output-format` | - | Force specific output format | `gepo url --output-format json` |
| `--verbose` | `-v` | Enable verbose output | `gepo url -v` |
| `--encoding` | - | Specify character encoding | `gepo url --encoding utf-8` |


## Detailed Examples

### HTTP Methods

```bash
# GET request
gepo GET https://api.example.com/users

# POST request
gepo POST https://api.example.com/users --json '{"name":"John"}'

# PUT request
gepo PUT https://api.example.com/users/1 --json '{"name":"John Updated"}'

# DELETE request
gepo DELETE https://api.example.com/users/1

# PATCH request
gepo PATCH https://api.example.com/users/1 --json '{"active":false}'

# HEAD request
gepo HEAD https://api.example.com/users

# OPTIONS request
gepo OPTIONS https://api.example.com/users
```

### Data Formats

```bash
# JSON data
gepo POST https://api.example.com/users --json '{"name":"John","age":30}'

# Form URL-encoded data
gepo POST https://api.example.com/form --form "name=John&age=30"

# Plain text data
gepo POST https://api.example.com/text --text "Hello, world!"

# HTML data
gepo POST https://api.example.com/html --html "<h1>Hello</h1><p>Content</p>"

# XML data
gepo POST https://api.example.com/xml --xml "<user><name>John</name></user>"
```

### File Operations

```bash
# Upload a file using multipart/form-data
gepo POST https://api.example.com/upload --file image.jpg --multipart

# Send file contents as request body
gepo POST https://api.example.com/documents --file document.txt

# Auto-detect content type from file extension
gepo POST https://api.example.com/data --file data.json

# Save response to file
gepo https://api.example.com/download --save response.txt

# Stream large file response
gepo https://api.example.com/large-file --stream --save large_file.zip
```

### Headers and Query Parameters

```bash
# Add custom headers
gepo https://api.example.com/users -H "X-API-Key: abc123" -H "Accept-Language: en-US"

# Add query parameters
gepo https://api.example.com/search -q "term=GEtPOst" -q "limit=10"

# Combine headers and query parameters
gepo https://api.example.com/search -H "Authorization: Bearer token123" -q "q=test"
```

### Authentication

```bash
# Basic authentication
gepo https://api.example.com/secure --auth "username:password"

# Digest authentication
gepo https://api.example.com/secure --auth "username:password" --auth-type digest

# Bearer token authentication
gepo https://api.example.com/secure --auth "token123" --auth-type bearer
```

### Cookies and Advanced Options

```bash
# Set cookies
gepo https://api.example.com/with-cookies --cookie "session=abc123" --cookie "user=john"

# Use a proxy
gepo https://api.example.com/users --proxy http://proxy.example.com:8080

# Disable SSL verification
gepo https://self-signed.example.com --no-verify

# Set request timeout
gepo https://slow-api.example.com/users --timeout 60

# Limit redirects
gepo https://redirect.example.com --max-redirects 2
```

### Output Formatting

```bash
# Force JSON output formatting
gepo https://api.example.com/users --output-format json

# Force plain text output
gepo https://api.example.com/users --output-format text

# Verbose output for debugging
gepo https://api.example.com/users -v
```

## Advanced Use Cases

### Piping Data

```bash
# Pipe data from a file to request body
cat data.json | gepo POST https://api.example.com/users --json

# Process the response with jq
gepo https://api.example.com/users | jq '.[] | select(.active==true)'
```

### Chaining Requests

```bash
# Use the response from one request in another
USER_ID=$(gepo POST https://api.example.com/users --json '{"name":"John"}' | jq -r '.id')
gepo https://api.example.com/users/$USER_ID
```

### File Upload Examples

```bash
# Upload a single file
gepo POST https://api.example.com/upload --file image.jpg --multipart

# Upload a file with custom field name
gepo POST https://api.example.com/upload -H "Content-Disposition: form-data; name=profile_picture; filename=avatar.png" --file avatar.png --multipart
```

### Streaming Examples

```bash
# Stream a large file download
gepo https://api.example.com/large-file --stream --save large_file.zip

# Display a streamed response in the terminal
gepo https://api.example.com/events --stream
```

## Troubleshooting

### Common Issues

- **SSL Verification Failed**: Use `--no-verify` if you're working with self-signed certificates
- **Timeout Errors**: Increase the timeout with `--timeout 60` for slow servers
- **Encoding Problems**: Specify the encoding with `--encoding utf-8`

### Debug Mode

For detailed troubleshooting, use the verbose flag:

```bash
gepo https://api.example.com/users -v
```

This displays the full request and response details including headers, timing, and more.

## Comparison with Similar Tools

| Feature | gepo | curl | httpie |
|---------|------|------|--------|
| JSON support | Built-in | Manual | Built-in |
| Form data | Built-in | Manual | Built-in |
| File uploads | Simple | Complex | Simple |
| Auth options | Basic, Digest, Bearer | Multiple | Multiple |
| Syntax | Simple | Complex | Simple |
| Output formatting | Auto/Manual | Manual | Auto |

## License

MIT License

--- 
Feel free to contact for any queries, Issues and suggestions. For contributing to GEPO, launch a PR and I will check it out.
For any kind of Issues, you may launch one on github Issues.
```
Created and managed by Baltej Singh
```
[@baltej223](github.com/baltej223)
