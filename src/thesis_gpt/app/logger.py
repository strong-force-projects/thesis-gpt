import logging
from datetime import datetime, timezone

import gspread
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
    def log(question: str, answer: str, native_lang: str | None) -> None:
        """Logs a question and its answer to the Google Sheet, with native language.

        Logging only occurs if the user has explicitly given consent.

        Args:
            question (str): The user’s question.
            answer (str): The chatbot’s response.
            native_lang (str | None): The user's native language, if provided.

        Raises:
            gspread.exceptions.APIError: If an unexpected error occurs when writing to the sheet.
        """
        if not ConsentManager.logging_allowed():
            return None

        try:
            sheet = Logger._get_sheet()
            sheet.append_row(
                [datetime.now(timezone.utc).isoformat(), question, answer, native_lang or ""]
            )
        except gspread.exceptions.APIError as e:
            if "Quota exceeded" in str(e) or "Rate Limit Exceeded" in str(e):
                system_logger.warning("Google Sheets quota exceeded — skipping log.")
            else:
                system_logger.warning(
                    f"Unexpected Google Sheets error: {e} — skipping log."
                )
