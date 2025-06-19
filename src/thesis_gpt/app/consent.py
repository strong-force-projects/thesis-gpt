import streamlit as st
from beartype import beartype


@beartype
class ConsentManager:
    @staticmethod
    def init():
        """
        Initialize consent state on first load.
        """
        if "allow_logging" not in st.session_state:
            st.session_state.allow_logging = None  # None = undecided

    @staticmethod
    def render():
        """
        Render the GDPR consent message and buttons.
        """
        if st.session_state.get("allow_logging") is not None:
            return None

        with st.expander("🔐 Data Collection Notice", expanded=True):
            st.markdown("""
            This chatbot logs your **questions**, **answers**, **public IP address**, and **approximate location** for research purposes only.

            We do **not** collect names, emails, or sensitive data unless you include them in your prompt.

            📜 Under [GDPR](https://gdpr.eu), you have the right to request deletion of your data at any time.

            🔓 **Logging is optional**. You can still use the chatbot even if you don’t consent.
            """)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ I consent to logging"):
                    st.session_state.allow_logging = True
                    st.rerun()
            with col2:
                if st.button("❌ No logging, thanks"):
                    st.session_state.allow_logging = False
                    st.rerun()

    @staticmethod
    def logging_allowed() -> bool:
        """
        Returns True if the user has consented to logging.
        """
        return st.session_state.get("allow_logging") is True

    @staticmethod
    def logging_status_badge():
        """
        Displays a small badge with the current logging status.
        """
        status = st.session_state.get("allow_logging")
        if status is True:
            st.markdown("✅ **Logging enabled**", unsafe_allow_html=True)
        elif status is False:
            st.markdown("🚫 **Logging disabled**", unsafe_allow_html=True)
