"""Types for ADCortex API"""
from dataclasses import dataclass

@dataclass
class UserInfo:
    user_id: str
    age: int
    gender: str
    location: str
    language: str
    interests: list[str]

@dataclass
class Platform:
    name: str
    version: str

@dataclass
class SessionInfo:
    session_id: str
    character_name: str
    character_metadata: dict
    user_info: UserInfo
    platform: Platform

@dataclass
class Message:
    role: str
    content: str

@dataclass
class Ad:
    idx: int
    ad_title: str
    ad_description: str
    placement_template: str
    link: str

