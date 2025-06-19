import streamlit as st

from thesis_gpt.app.consent import ConsentManager
from thesis_gpt.app.logger import Logger
from thesis_gpt.retrieval.retriever import ThesisRetriever

response_generator = ThesisRetriever()

# Page setup
st.set_page_config(page_title="Thesis Chat", layout="centered")

ConsentManager.init()
ConsentManager.render()
ConsentManager.logging_status_badge()

# Info box
if "show_info" not in st.session_state:
    st.session_state.show_info = True

if st.session_state.show_info:
    with st.expander("ℹ️ About this chatbot", expanded=True):
        st.markdown("""
        - This is an MVP, there are many ideas for improvements.
        - This chatbot is **stateless** — it does not remember previous messages.  
          Follow-up questions may not be understood unless they’re self-contained.
        - The model **cannot interpret or retrieve images** from the thesis.  
          If a section refers to a figure, the assistant may describe its caption only.
        - It does best with **specific** questions, rather than broad **summarizing** questions. 
        - The responses are based entirely on the content of the thesis.
        - Code available [here](https://github.com/strong-force-projects/thesis-gpt).
        """)

st.title("🎓 Chat with Boje's PhD Thesis", anchor=False)

# State init
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_response" not in st.session_state:
    st.session_state.pending_response = False
if "suggestions_shown" not in st.session_state:
    st.session_state.suggestions_shown = True


# Backend

if st.session_state.suggestions_shown:
    # 💡 Suggested Questions
    st.markdown("#### 💡 Suggested Questions")

    suggestions = [
        "What is MultiMix?",
        "Who is in the Doctoral Committee?",
        "What are some key limitations?",
        "What loss function is used in MultiMix?",
    ]

    cols = st.columns(len(suggestions))
    for col, suggestion in zip(cols, suggestions):
        if col.button(suggestion):
            st.session_state.history.append((suggestion, ""))
            st.session_state.pending_response = True
            st.session_state.suggestions_shown = False
            st.rerun()

# Handle pending response from suggestion or rerun
if st.session_state.pending_response:
    query, _ = st.session_state.history[-1]
    with st.spinner("Thinking..."):
        answer = ThesisRetriever.retrieve(query)
    st.session_state.history[-1] = (query, answer)
    st.session_state.pending_response = False
    Logger.log(query, answer)

# Manual chat input
query = st.chat_input("Ask something about the thesis...")
if query:
    st.session_state.history.append((query, ""))
    st.session_state.pending_response = True
    st.session_state.suggestions_shown = False
    st.rerun()

# Display chat history
for q, a in st.session_state.history:
    st.chat_message("user").write(q)
    if a:
        st.chat_message("assistant").write(a)
