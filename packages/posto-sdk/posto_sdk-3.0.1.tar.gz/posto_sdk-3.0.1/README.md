Viral X Machine

The Posto SDK makes it easy to schedule and post your content on social media networks through a simple Python API. You can post messages immediately or schedule them for later, attach media files (images, videos), and much more.

Get started by installing the SDK:

pip install posto-sdk

Then, import the SDK into your Python script:

from posto_sdk.posto_sdk import PostoSDK

Authentication

The SDK supports two modes of authentication:

    Using username and password:
    This creates a Base64 encoded token automatically.

    Using an already encoded token:

Using Username & Password

# Create an instance using your WordPress username and password
posto = PostoSDK.from_credentials(username="your_username", password="your_password")

Using an Existing Token

# Create an instance if you already have a Base64 encoded token
posto = PostoSDK.from_token(token="your_base64_encoded_token")

Posting a Message

The core method for posting is post(). It accepts a message along with several optional keyword parameters that control target channels, scheduling, media attachments, and network settings.
Parameters

    message (str)
    The text content you want to post.

    to (int, str, or list)
    Specifies the channel(s) by which to post. Pass the channel ID (int) or name (str) or a list of them.

        Example: to=2, to="News Feed", or to=[2, "Blog"].

    when (datetime, str, or int, optional)
    Define when to post your message:

        Immediate posting: Set to "now" or omit this parameter.

        Relative time string: Use a string like "30m" for 30 minutes, "1h" for 1 hour, or "2d" for 2 days from now.

        Specific datetime: Pass a datetime object or a Unix timestamp (int).

    media (str or list, optional)
    Path(s) or URL(s) to media files (images, videos) to attach. Accepts a single file (string) or a list of files.

    settings (dict, optional)
    Custom network settings to override the defaults for each channel’s post. See the Custom Network Settings section for more details.

Immediate Post

Post a message immediately to a single channel.

# Post an immediate message to channel with ID 2
result = posto.post("Hello World!", to=2)
print(result)

Scheduled Post (Relative Time)

Schedule a post to be published in, for example, 1 hour.

# Post a message scheduled 1 hour from now to channels 2 and 3
result = posto.post("Scheduled post in 1 hour", to=[2, 3], when="1h")
print(result)

Scheduled Post (Specific DateTime)

Schedule the post for a specific future datetime.

from datetime import datetime, timedelta

# Schedule a post 2 days from now
future_time = datetime.now() + timedelta(days=2)

result = posto.post("Post scheduled for a specific datetime", to=[2, 3], when=future_time)
print(result)

Post with Media Attachment

You can easily attach media (local file path or URL) along with your message.

# Post with an image attached that will be published in 1 hour
result = posto.post("Check out this cool photo!", to=[2, 3], media="path/to/image.jpg", when="1h")
print(result)

For multiple media attachments, pass a list:

result = posto.post("Multiple images attached!", to="BlogChannel", media=["image1.jpg", "image2.jpg"])
print(result)

Custom Network Settings

Override default network settings (if necessary) by passing a settings dictionary. The keys in this dictionary depend on the specific network, but common options include toggles for attaching links, cutting post text, etc.

# Custom settings for the target network
custom_settings = {
    "attach_link": False,      # Do not attach a link by default
    "cut_post_text": True,     # Shorten the post text if necessary
    "custom_option": "value"   # Any additional settings your network may require
}

result = posto.post("Post with custom settings", to=2, settings=custom_settings)
print(result)

Querying Channels and Network Info

You can easily retrieve details about available channels and network settings.

    List all channels:

channels = posto.channels
print(channels)

    Get a channel by ID:

channel = posto.get_channel(2)
print(channel)

    Find channel(s) by name (case-insensitive):

matching_channels = posto.get_channel_by_name("news")
print(matching_channels)

    List available social networks:

networks = posto.get_networks()
print(networks)

Additionally, methods such as get_network_settings(), save_network_settings(), and others allow you to retrieve and manipulate network-specific settings.
Error Handling

The SDK raises custom exceptions to help you manage errors:

    MediaUploadError: Raised when media uploading fails.

    ChannelError: Raised for channel-related issues.

    PostingError: Raised if the post creation fails.

Always handle or log errors when calling post():

try:
    result = posto.post("Test post", to=2)
    print(result)
except Exception as e:
    print("An error occurred:", e)

Example Code

Below is a complete example that combines several of the features described above.

from datetime import datetime, timedelta
from posto_sdk.posto_sdk import PostoSDK

# Initialize the SDK with your credentials
posto = PostoSDK.from_credentials(username="your_username", password="your_password", debug=True)

# 1. Immediate post
result_immediate = posto.post("Hello World!", to=2)
print("Immediate post result:", result_immediate)

# 2. Scheduled post using a relative time string ("1h" means 1 hour from now)
result_scheduled_rel = posto.post("Scheduled post in 1 hour", to=[2, 3], when="1h")
print("Scheduled (relative) post result:", result_scheduled_rel)

# 3. Scheduled post using a specific datetime (2 days from now)
future_time = datetime.now() + timedelta(days=2)
result_scheduled_dt = posto.post("Post scheduled for specific datetime", to=[2, 3], when=future_time)
print("Scheduled (datetime) post result:", result_scheduled_dt)

# 4. Post with media attachment
result_media = posto.post("Check out this cool photo!", to=[2, 3], media="path/to/image.jpg", when="1h")
print("Post with media result:", result_media)

# 5. Post with custom network settings
custom_settings = {
    "attach_link": False,
    "cut_post_text": True,
    "custom_option": "value"
}
result_custom = posto.post("Post with custom settings", to=2, settings=custom_settings)
print("Post with custom settings result:", result_custom)

PostoSDK - Network Settings & Capabilities Documentation

This section of the PostoSDK empowers you to manage and configure network-specific settings and capabilities with ease. You can:

    Retrieve available networks from your backend.

    Fetch, validate, and update network settings.

    Access network capabilities such as media support and text length limits.

    Save and manage settings profiles across multiple networks.

To start managing network settings, initialize the NetworkSettingsManager by providing your authentication token.

from posto_sdk.network_settings import NetworkSettingsManager

# Replace this with your authentication token.
auth_token = "your_auth_token"

# Initialize the NetworkSettingsManager.
network_manager = NetworkSettingsManager(auth_token)

Method Overview
Retrieving Available Networks

Use get_available_networks() to fetch a list of social networks configured on your backend. Each network includes attributes like the network slug, name, and icon.

networks = network_manager.get_available_networks()
for network in networks:
    print(f"Network: {network['name']} (Slug: {network['slug']})")

Getting Network Settings

Fetch network-specific settings by calling get_network_settings(network). This method returns a NetworkSettings object with several helpful methods:

    get_available_settings(): Retrieve the current values of all settings for a network.

    get_default_settings(): Retrieve the default values for each setting.

    to_dict(): Convert settings into a dictionary useful for API requests.

# For example, get settings for the 'facebook' network.
facebook_settings_obj = network_manager.get_network_settings("facebook")

# Retrieve the current settings.
current_settings = facebook_settings_obj.get_available_settings()
print("Current Facebook Settings:", current_settings)

# Retrieve the default settings.
default_settings = facebook_settings_obj.get_default_settings()
print("Default Facebook Settings:", default_settings)

Validating Network Settings

Before saving any changes, validate the settings using validate_network_settings(network, settings). This function checks, for example, if the post text length exceeds the maximum allowed or if media uploads are supported by the network.

settings_to_validate = {
    "post_text": "Hello, world!",
    "upload_media": True
}

try:
    network_manager.validate_network_settings("facebook", settings_to_validate)
    print("Settings are valid!")
except ValueError as err:
    print("Validation Error:", err)

Saving Network Settings

After validation, update the network settings by calling save_network_settings(network, settings). This method converts a NetworkSettings object to a dictionary if needed, validates the settings, and then sends them to the backend.

updated_settings = {
    "post_text": "Updated post text for Facebook!",
    "upload_media": False
}

# Save the new settings for 'facebook'
network_manager.save_network_settings("facebook", updated_settings)
print("Facebook settings have been saved successfully!")

Working with Network Capabilities

You can also retrieve network capabilities—which include information like media support and maximum text length—using get_network_capabilities(network). These capabilities help you ensure that the settings you provide are supported by the network.

capabilities = network_manager.get_network_capabilities("facebook")
print("Supports Media:", capabilities.supports_media)
print("Max Text Length:", capabilities.max_text_length)

Managing Settings Profiles

The SDK supports saving and retrieving settings profiles. A profile allows you to maintain a standard set of settings for multiple networks.

Saving a Settings Profile

profile_settings = {
    "facebook": {"post_text": "Profile post for Facebook", "upload_media": True},
    "twitter": {"post_text": "Profile post for Twitter!"}
}

network_manager.save_settings_profile("daily_posts", profile_settings)
print("Settings profile 'daily_posts' saved.")

Retrieving a Settings Profile

profile = network_manager.get_settings_profile("daily_posts")
print("Retrieved Profile:", profile)

Listing All Profiles

profiles = network_manager.list_settings_profiles()
print("Available Profiles:", profiles)

Example Usage

Below is a complete example that demonstrates how to initialize the manager, list networks, update settings, and manage a settings profile:

from posto_sdk.network_settings import NetworkSettingsManager

# 1. Initialize the NetworkSettingsManager.
base_url = "https://example.com"
auth_token = "your_auth_token"
network_manager = NetworkSettingsManager(base_url, auth_token)

# 2. List available networks.
networks = network_manager.get_available_networks()
print("Available Networks:")
for network in networks:
    print(network)

# 3. Get current settings for the 'facebook' network.
facebook_settings = network_manager.get_network_settings("facebook")
print("Current Facebook Settings:", facebook_settings.get_available_settings())

# 4. Validate and update settings for 'facebook'.
new_settings = {
    "post_text": "This is my updated Facebook post!",
    "upload_media": True
}

try:
    network_manager.validate_network_settings("facebook", new_settings)
    network_manager.save_network_settings("facebook", new_settings)
    print("Facebook settings updated successfully.")
except ValueError as ve:
    print("Error updating Facebook settings:", ve)

# 5. Create and retrieve a settings profile for multiple networks.
profile = {
    "facebook": {"post_text": "Profile post for Facebook", "upload_media": False},
    "twitter": {"post_text": "Profile post for Twitter!"}
}

network_manager.save_settings_profile("profile_example", profile)
retrieved_profile = network_manager.get_settings_profile("profile_example")
print("Retrieved Profile:", retrieved_profile)

Parameter Descriptions

    auth_token: The authentication token used for your API requests.

    network: A string identifier for a social network (e.g., "facebook", "twitter").

    settings (dict): A dictionary containing network settings. Common keys include:

        post_text: Content for the post.

        upload_media: A boolean flag to indicate if media should be uploaded.

    profile name: A unique name used to identify a settings profile.

    profile settings (dict): A dictionary that maps network identifiers to their respective settings.

Additional Notes

    Default Behavior: If no specific data is provided from the API, the SDK uses fallback defaults (e.g., treating settings as optional).

    Cache Management: The SDK caches network settings and capabilities to speed up operations. Use clear_cache(network) to clear the cache for a specific network or clear_cache() to clear it globally.

    Error Handling: Methods such as validate_network_settings will raise a ValueError if the settings do not meet the network requirements (for instance, if a post's text exceeds the allowed maximum length).

ScheduleManager Documentation

This guide provides an overview of the ScheduleManager class, which allows you to manage schedules through the SDK. With ScheduleManager, you can:

    List schedules with a variety of filtering options.

    Retry failed schedules.

    Delete schedules based on specific criteria.

Prerequisites

    Installation: Make sure you have installed the SDK package in your project.

Instantiation

First, create an instance of ScheduleManager by passing your API client object.

from posto_sdk.schedule_manager import ScheduleManager
from your_api_client_library import APIClient  # Replace with your actual API client import

# Initialize your API client
api_client = APIClient(api_key="YOUR_API_KEY", base_url="https://api.example.com")

# Create an instance of ScheduleManager
schedule_manager = ScheduleManager(api_client)

Methods
1. Listing Schedules

The list() method retrieves a list of schedules with optional filtering parameters.

Parameters

    status:
    Filter by schedule status. Accepts a string (e.g., "error") or a list of statuses (e.g., ["error", "draft"]). Valid statuses include:
    (\texttt{"error"}), (\texttt{"not_sent"}), (\texttt{"sending"}), (\texttt{"success"}), (\texttt{"draft"}).

    network:
    Filter by social network(s). Accepts a string or a list of strings.

    page (int, default: 1):
    The page number used for pagination.

    per_page (int, default: 10):
    Number of items per page.

    schedule_id (int, optional):
    Filter by a specific schedule ID.

    group_id (str, optional):
    Filter by a specific schedule group ID.

Usage Example

# List schedules using default pagination
response = schedule_manager.list()
print("All Schedules:", response)

# List schedules filtering by a specific status and network
response = schedule_manager.list(status="error", network=["facebook", "twitter"])
print("Filtered Schedules:", response)

# List schedules for a specific schedule ID
response = schedule_manager.list(schedule_id=123)
print("Specific Schedule:", response)

2. Retrying Schedules

The retry() method attempts to retry the processing of failed schedules.

Parameters

    schedules:
    A single schedule ID (integer) or a list of schedule IDs to retry.

Usage Example

# Retry a single schedule
response = schedule_manager.retry(123)
print("Retry Response (single schedule):", response)

# Retry multiple schedules at once
response = schedule_manager.retry([123, 124, 125])
print("Retry Response (multiple schedules):", response)

3. Deleting Schedules

The delete() method deletes schedules matching provided criteria.

Parameters

    schedule_ids (List[int], optional):
    List of specific schedule IDs to delete.

    exclude_ids (List[int], optional):
    List of schedule IDs to be excluded from deletion.

    status (str or List[str], optional):
    Delete schedules with the given status (or statuses).

    older_than (str, optional):
    Delete schedules older than the specified time. Use a formatted string such as:

        "7d" for 7 days,

        "24h" for 24 hours,

        "30m" for 30 minutes.
        The system calculates the date by subtracting this duration from the current date.

    all (bool, default: False):
    If set to True, delete all schedules that match the other provided criteria.

Note:
If all is not set to True, you must specify at least one filtering parameter (schedule_ids, status, or older_than). Otherwise, a ValueError will be raised.

Usage Example

# Delete schedules by specific schedule IDs
result = schedule_manager.delete(schedule_ids=[101, 102])
print("Delete Result (specific IDs):", result)

# Delete schedules that have a specific status (e.g., "draft")
result = schedule_manager.delete(status="draft")
print("Delete Result (by status):", result)

# Delete schedules older than 7 days
result = schedule_manager.delete(older_than="7d")
print("Delete Result (older than 7 days):", result)

# Delete all schedules matching certain conditions
result = schedule_manager.delete(status=["error", "draft"], all=True)
print("Delete Result (all conditions):", result)

Error Handling

    The delete() method will log an error and return False if an exception is encountered during the deletion process.

    For any invalid input (e.g., incorrect format for older_than), a ValueError will be raised.

Make sure to handle these cases appropriately in your application.
Social Media Manager SDK Usage Guide

This guide covers the basics of using the SocialMediaManager class, which extends the base PostoSDK to simplify managing social media channels. You will learn how to initialize the SDK, set default posting options, post messages, schedule campaigns, and manage custom post styles.
1. Installation

Make sure you have installed the SDK and its dependencies. Then, you can import the SocialMediaManager in your project:

from posto_sdk.social_media_manager import SocialMediaManager

2. Initialization

Initialize the SocialMediaManager with your WordPress (or corresponding service) credentials. The credentials are used to create an authentication token.

# Initialize the SocialMediaManager with your credentials
manager = SocialMediaManager(username="your_username", password="your_password")

3. Setting Default Post Settings

You can globally define post settings that apply to all channels of a network or to a specific channel.
3.1. Set Network Defaults

Use set_network_defaults to define defaults for a particular network (such as Twitter, Facebook, TikTok, etc.). These settings will apply to all channels within that network.

manager.set_network_defaults("twitter", {
    "post_text": "🚨 {post_title} 🚨",
    "cut_post_text": True
})

3.2. Set Channel Defaults

For channel-specific settings, use set_channel_defaults. If you pass a channel name, the method will find the corresponding channel ID.

manager.set_channel_defaults("my_business_instagram", {
    "post_text": "{post_title}\n.\n.\n.\n#business #updates",
    "upload_media": True
})

4. Posting Messages

There are several ways to post messages using the SDK. Choose the one that best fits your needs.
4.1. Quick Post

Post a message immediately to all active channels.

Method Signature

quick_post(message: str, image: Optional[str] = None, style: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> bool

    message: The post content.

    image: A path (or URL) to an image file (if any).

    style: Predefined style name (e.g., "announcement", "blog", or "product").

    settings: A dictionary with network-specific overrides.

Example

success = manager.quick_post(
    "Hello world! Check out our latest update!",
    image="path/to/image.jpg",
    style="announcement"
)

if success:
    print("Post was successful!")
else:
    print("Post failed; please check your configuration.")

4.2. Post to Specific Platforms

Use post_to to send a post to selected platforms. This method supports scheduling with the when parameter as well.

Method Signature

post_to(
    platforms: Union[str, List[str]], 
    message: str, 
    image: Optional[str] = None, 
    when: Optional[str] = None,
    style: Optional[str] = None, 
    settings: Optional[Dict[str, Any]] = None
) -> bool

    platforms: A single platform (e.g., "twitter") or a list of platforms (e.g., ["facebook", "instagram"]).

    message: The text to post.

    image: Optional image path or URL.

    when: Schedule the post (e.g., "tomorrow", "tonight", "30m", "1h", "2d").

    style: Predefined style (as in quick_post).

    settings: A dictionary of custom settings for refining the post.

Example

result = manager.post_to(
    platforms="twitter",
    message="Check out our new offer!",
    image="offer.jpg",
    when="1h",
    style="product",
    settings={
        "twitter": {"post_text": "🔥 {post_title} 🔥"}
    }
)

if result:
    print("Post scheduled successfully!")

4.3. Scheduling a Post

Schedule a post for a later time using the schedule_post method.

Method Signature

schedule_post(
    message: str, 
    when: str, 
    image: Optional[str] = None, 
    platforms: Optional[List[str]] = None,
    style: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None
) -> bool

    when: Can be friendly strings like "tomorrow" or "tonight", or a relative time like "30m", "1h", or "2d".

Example

scheduled = manager.schedule_post(
    "Don't miss tomorrow's exclusive sale!",
    when="tomorrow",
    style="announcement"
)

if scheduled:
    print("Post scheduled for tomorrow!")
else:
    print("Scheduling failed.")

4.4. Creating a Campaign

A campaign is a series of posts scheduled over time.

Method Signature

create_campaign(
    messages: List[str], 
    platforms: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    start_time: Optional[str] = None,
    hours_between_posts: int = 24,
    style: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None
) -> List[bool]

    messages: List of messages.

    platforms: List of target platforms. If omitted, the campaign is posted to all available networks.

    images: Optional list of image paths/URLs for each post.

    start_time: When the campaign should start (e.g., "tomorrow" or "tonight").

    hours_between_posts: Interval between each post (default is 24 hours).

    style: Predefined style.

    settings: Network-specific custom settings.

Example

messages = [
    "Campaign Day 1: Launch announcement! 🚀",
    "Campaign Day 2: Product feature update!",
    "Campaign Day 3: Customer success story!"
]

campaign_results = manager.create_campaign(
    messages=messages,
    start_time="tomorrow",
    hours_between_posts=24,
    style="blog"
)

if all(campaign_results):
    print("Campaign scheduled successfully!")
else:
    print("Some posts in the campaign failed to schedule.")

4.5. Creating a Quick Campaign

For a faster setup with sensible defaults, you can use create_quick_campaign.

Method Signature

create_quick_campaign(
    messages: List[str], 
    interval: str = "1d", 
    start_time: Optional[str] = None
) -> bool

    interval: Time between posts given as "1d", "1h", etc.

    start_time: When the campaign should begin (e.g., "tomorrow").

Example

quick_messages = [
    "Quick Campaign Day 1: Special announcement 🚀",
    "Quick Campaign Day 2: More details coming soon!",
    "Quick Campaign Day 3: Stay tuned for updates!"
]

if manager.create_quick_campaign(quick_messages, interval="1d", start_time="tomorrow"):
    print("Quick campaign scheduled successfully!")
else:
    print("Quick campaign scheduling failed.")

5. Customizing Post Styles

You can save and reuse custom post styles, which is very helpful if you frequently use specific formatting across different platforms.
5.1. Saving a Style

Method Signature

save_style(name: str, settings: Dict[str, Dict[str, Any]]) -> None

    name: A unique name for your style.

    settings: A dictionary mapping social network identifiers (e.g., "twitter", "facebook") to their settings.

Example

manager.save_style("my_announcement", {
    "twitter": {"post_text": "🎯 {post_title}", "cut_post_text": True},
    "facebook": {"post_text": "📢 Important Update:\n\n{post_title}", "attach_link": True}
})

5.2. Retrieving and Listing Styles

    Get a saved style:

style_settings = manager.get_style("my_announcement")

List all available styles:

    available_styles = manager.list_styles()
    print("Available Styles:", available_styles)

6. Managing Channels & Defaults

Access your channels and review or clear default settings as needed.
6.1. Getting Channels

# Get all channels
all_channels = manager.get_channels()

# Filter channels by platform (e.g., Twitter)
twitter_channels = manager.get_channels("twitter")

6.2. Viewing & Clearing Defaults

# Get network defaults for TikTok
tiktok_defaults = manager.get_network_defaults("tiktok")

# Get channel defaults (passing either an ID or channel name)
instagram_defaults = manager.get_channel_defaults("my_instagram")

# Clear defaults for a specific network
manager.clear_defaults(network="twitter")

# Clear defaults for a specific channel
manager.clear_defaults(network="facebook", channel_id="my_facebook_channel")

7. Deleting Scheduled Posts

Manage your scheduled posts by deleting unwanted schedules.
7.1. Delete All Schedules with Filters

# Delete all pending (not sent) schedules for Twitter, excluding specific IDs if needed:
manager.delete_all_schedules(
    platforms=["twitter"],
    statuses=["not_sent"],
    exclude_ids=[123, 456]  # Optional: list IDs you want to keep
)

7.2. Delete Specific Scheduled Posts

# Delete specific schedule IDs
manager.delete_schedules([789, 1011])

8. Complete Example

Below is a simple script that brings many of these features together:

from posto_sdk.social_media_manager import SocialMediaManager

# Initialize SocialMediaManager
manager = SocialMediaManager(username="your_username", password="your_password")

# Set defaults for Twitter
manager.set_network_defaults("twitter", {
    "post_text": "🚨 Breaking News: {post_title} 🚨",
    "cut_post_text": True
})

# Save a custom style for announcements
manager.save_style("my_announcement", {
    "twitter": {"post_text": "🎯 {post_title}", "cut_post_text": True},
    "facebook": {"post_text": "📢 Important Update:\n\n{post_title}", "attach_link": True}
})

# Make a quick post to all active channels
if manager.quick_post("Hello world! This is a quick update.", image="hello.jpg", style="my_announcement"):
    print("Quick post sent successfully!")
else:
    print("Quick post failed; check logs for details.")

# Schedule a post for tomorrow with custom settings
if manager.schedule_post(
    "Don't miss our exclusive sale tomorrow!",
    when="tomorrow",
    style="announcement"
):
    print("Post scheduled for tomorrow!")
else:
    print("Failed to schedule the post.")

# Launch a campaign with multiple scheduled posts
messages = [
    "Day 1: Launch announcement! 🚀",
    "Day 2: Feature spotlight ✨",
    "Day 3: Customer testimonials 💬"
]
campaign_results = manager.create_campaign(
    messages=messages,
    start_time="tomorrow",
    hours_between_posts=24,
    style="blog"
)
if all(campaign_results):
    print("Campaign scheduled successfully!")
else:
    print("Some campaign posts failed to schedule.")

Last updated 19 hours ago
