import logging
from datetime import datetime, timezone

import gspread
import requests
import streamlit as st
from beartype import beartype
from google.oauth2.service_account import Credentials

from thesis_gpt.app.consent import ConsentManager

system_logger = logging.getLogger(__name__)


@beartype
class Logger:
    """Handles logging chatbot interactions to a Google Sheet."""

    SHEET_NAME = "thesis_chat_log"
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    @staticmethod
    @st.cache_resource
    def _get_sheet() -> gspread.Worksheet:
        """Initializes and caches the Google Sheet client.

        Returns:
            gspread.Worksheet: The worksheet object for logging.
        """
        creds = Credentials.from_service_account_info(
            st.secrets["gcp"], scopes=Logger.SCOPES
        )
        client = gspread.authorize(creds)
        return client.open(Logger.SHEET_NAME).sheet1

    @staticmethod
    def _get_ip_and_location() -> tuple[str, str]:
        """Attempts to retrieve the public IP and location of the user.

        Returns:
            tuple[str, str]: A tuple containing the IP address and a location string
                             formatted as 'City, Country'. Defaults to 'unknown' values.
        """
        try:
            res = requests.get("https://ipinfo.io/json", timeout=3)
            if res.status_code == 200:
                data = res.json()
                ip = data.get("ip", "unknown")
                location = f"{data.get('city', '')}, {data.get('country', '')}".strip(
                    ", "
                )
                return ip, location
        except requests.RequestException:
            pass
        return "unknown", "unknown"

    @staticmethod
    def log(question: str, answer: str) -> None:
        """Logs a question and its answer to the Google Sheet, with IP and location metadata.

        Logging only occurs if the user has explicitly given consent.

        Args:
            question (str): The user’s question.
            answer (str): The chatbot’s response.

        Raises:
            gspread.exceptions.APIError: If an unexpected error occurs when writing to the sheet.
        """
        if not ConsentManager.logging_allowed():
            return None

        try:
            sheet = Logger._get_sheet()
            ip, location = Logger._get_ip_and_location()
            sheet.append_row(
                [datetime.now(timezone.utc).isoformat(), question, answer, ip, location]
            )
        except gspread.exceptions.APIError as e:
            if "Quota exceeded" in str(e) or "Rate Limit Exceeded" in str(e):
                system_logger.warning("Google Sheets quota exceeded — skipping log.")
            else:
                system_logger.warning(
                    f"Unexpected Google Sheets error: {e} — skipping log."
                )
