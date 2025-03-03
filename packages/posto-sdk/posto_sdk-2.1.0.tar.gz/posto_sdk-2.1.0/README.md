# Posto SDK Documentation

## Overview

Posto SDK is a powerful Python library for managing and automating social media posts across multiple platforms. It provides a simple, unified interface for scheduling posts, managing media uploads, and handling different social network configurations.

## Installation

```bash
pip install posto-sdk
```

## Quick Start

```python
from posto_sdk import PostoSDK

# Initialize with username and password
sdk = PostoSDK.from_credentials(username="your_username", password="your_password")

# Or initialize with an existing token
sdk = PostoSDK.from_token(token="your_auth_token")

# Schedule a simple post
result = sdk.post(
    message="Hello World!",
    channels=[1, 2],  # Channel IDs
    media=["path/to/image.jpg"],  # Optional media
    when="2024-03-01 15:00:00"  # Optional scheduling
)
```

## Core Features

### Authentication

The SDK supports two authentication methods:

1. Username/Password Authentication:
```python
sdk = PostoSDK.from_credentials(username="your_username", password="your_password")
```

2. Token-based Authentication:
```python
sdk = PostoSDK.from_token(token="your_auth_token")
```

### Channel Management

```python
# Get all available channels
channels = sdk.get_available_channels()

# Get channels by network type
facebook_channels = sdk.get_channels_by_type("facebook")

# Find channels by name
channel = sdk.get_channel_by_name("My Facebook Page")

# Get active channels
active_channels = sdk.get_active_channels()

# Refresh channel list
sdk.refresh_channels()
```

### Posting Content

#### Simple Post
```python
result = sdk.post(
    message="Hello World!",
    channels=1  # Single channel ID
)
```

#### Post with Media
```python
result = sdk.post(
    message="Check out these photos!",
    channels=[1, 2],  # Multiple channel IDs
    media=[
        "path/to/image1.jpg",
        "https://example.com/image2.jpg"  # URLs are supported
    ]
)
```

#### Scheduled Post
```python
from datetime import datetime, timedelta

# Schedule for tomorrow
tomorrow = datetime.now() + timedelta(days=1)
result = sdk.schedule_post(
    message="Scheduled post",
    channels=[1, 2],
    media=["path/to/image.jpg"],
    when=tomorrow
)
```

### Media Management

The SDK supports various media types:

- Images: JPEG, PNG, GIF, WebP, TIFF, BMP
- Videos: MP4, MPEG, QuickTime, AVI, WMV, WebM, 3GPP

```python
# Upload single media
media_ids = sdk.upload_media("path/to/image.jpg")

# Upload multiple media files
media_ids = sdk.upload_media([
    "path/to/image1.jpg",
    "https://example.com/image2.jpg",
    "path/to/video.mp4"
])
```

### Network Settings and Capabilities

```python
# Get available networks
networks = sdk.get_networks()

# Get network capabilities
capabilities = sdk.get_network_capabilities("facebook")

# Get network defaults
defaults = sdk.get_network_defaults("twitter")

# Get supported media types for a network
media_types = sdk.get_supported_media_types("instagram")
```

### Settings Profiles

```python
# Save settings profile
settings = {
    "facebook": {"image_quality": "high"},
    "twitter": {"auto_hashtags": True}
}
sdk.save_settings_profile("my_profile", settings)

# Get settings profile
profile = sdk.get_settings_profile("my_profile")

# List all profiles
profiles = sdk.list_settings_profiles()
```

## Response Handling

The SDK uses structured response objects:

```python
result = sdk.post(message="Hello", channels=1)

if result.success:
    print(f"Posted successfully! Schedule Group ID: {result.schedule_group_id}")
else:
    print(f"Posting failed: {result.error_message}")
```

## Error Handling

The SDK provides specific exception classes for better error handling:

```python
from posto_sdk import PostoError, MediaUploadError, ChannelError, PostingError

try:
    result = sdk.post(message="Hello", channels=1)
except MediaUploadError as e:
    print(f"Media upload failed: {e}")
except ChannelError as e:
    print(f"Channel error: {e}")
except PostingError as e:
    print(f"Posting failed: {e}")
except PostoError as e:
    print(f"General error: {e}")
```

## Advanced Features

### Debug Mode

Enable debug mode for detailed logging:

```python
sdk = PostoSDK.from_token(token="your_token", debug=True)
```

### Custom Base URL

If you're using a custom installation:

```python
sdk = PostoSDK.from_token(
    token="your_token",
    base_url="https://your-custom-domain.com"
)
```

### Network-Specific Settings

```python
result = sdk.post(
    message="Hello World!",
    channels=1,
    network_settings={
        "facebook": {
            "privacy": "friends",
            "allow_comments": True
        },
        "twitter": {
            "reply_settings": "followers"
        }
    }
)
```

## Best Practices

1. **Error Handling**: Always implement proper error handling using the provided exception classes.
2. **Media Upload**: Use appropriate media formats supported by target networks.
3. **Rate Limiting**: Consider implementing rate limiting in your application when making multiple requests.
4. **Token Security**: Store authentication tokens securely and never expose them in your code.
5. **Channel Validation**: Validate channel IDs before posting to ensure they are active and accessible.

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/yourusername/posto-sdk).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Compiling with Nuitka

This SDK can be compiled using Nuitka for enhanced protection and distribution. Two compilation methods are available:

### Standard Compilation

For standard compilation with basic protection:

```bash
python compile_with_nuitka.py
```

This creates a compiled version of the SDK in the `dist` directory, ready for PyPI distribution.

### Advanced Compilation

For advanced compilation with stronger protection:

```bash
python compile_with_nuitka_advanced.py
```

The advanced compilation includes additional security measures such as:
- Disabled bytecode caching
- Removed docstrings and assertions
- Isolated Python mode
- Removed embedded files

Note: Advanced protection may have a small performance impact. Test thoroughly before distribution.

## Pure Python Obfuscation

As an alternative to Nuitka compilation, you can use our pure Python obfuscation scripts:

### Basic Obfuscation

For basic variable renaming and comment removal:

```bash
python obfuscate_sdk.py
```

### Advanced Obfuscation

For stronger protection including string literal encoding and runtime verification:

```bash
python obfuscate_sdk_advanced.py
```

The advanced obfuscation includes:
- Variable, function, and class renaming
- String literal encoding
- Docstring and comment removal
- Runtime verification to detect debugging attempts
- Anti-tampering measures

### Publishing to PyPI

After obfuscation, you can build and publish the package to PyPI:

```bash
cd dist
python -m build
python -m twine upload dist/*
```

Make sure you have the necessary PyPI credentials configured.
