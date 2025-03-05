"""Types for ADCortex API.

This module defines data classes used by the ADCortex API client.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class UserInfo:
    """
    Stores user information for ADCortex API.

    Attributes:
        user_id (str): Unique identifier for the user.
        age (int): User's age.
        gender (str): User's gender.
        location (str): User's location.
        language (str): Preferred language.
        interests (List[str]): A list of user's interests.
    """
    user_id: str
    age: int
    gender: str
    location: str
    language: str
    interests: List[str]


@dataclass
class Platform:
    """
    Contains platform-related metadata.

    Attributes:
        name (str): Name of the platform.
        version (str): Version of the platform.
    """
    name: str
    version: str


@dataclass
class SessionInfo:
    """
    Stores session details including user and platform information.

    Attributes:
        session_id (str): Unique identifier for the session.
        character_name (str): Name of the character (assistant).
        character_metadata (Dict[str, Any]): Additional metadata for the character.
        user_info (UserInfo): User information.
        platform (Platform): Platform details.
    """
    session_id: str
    character_name: str
    character_metadata: Dict[str, Any]
    user_info: UserInfo
    platform: Platform


@dataclass
class Message:
    """
    Represents a single message in a conversation.

    Attributes:
        role (str): The role of the message sender (e.g., 'user', 'ai').
        content (str): The content of the message.
    """
    role: str
    content: str


@dataclass
class Ad:
    """
    Represents an advertisement fetched via the ADCortex API.

    Attributes:
        idx (int): Identifier for the ad.
        ad_title (str): Title of the advertisement.
        ad_description (str): Description of the advertisement.
        placement_template (str): Template used for ad placement.
        link (str): URL link to the advertised product or service.
    """
    idx: int
    ad_title: str
    ad_description: str
    placement_template: str
    link: str
