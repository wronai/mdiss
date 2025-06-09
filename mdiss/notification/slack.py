"""
Slack notification service for mdiss.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

import requests

from ..models import Category, FailedCommand, Priority


class SlackNotificationService:
    """Service for sending Slack notifications."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session = requests.Session()

    def send_failure_summary(self, commands: List[FailedCommand],
                           title: str = "Build Failures Detected") -> bool:
