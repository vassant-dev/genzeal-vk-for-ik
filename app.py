import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from src.prmuni import GitHubRepository, SimpleReviewer

TITLE = "PR Muni"
SUB_TITLE = "An LLM based pull request reviewer."
REPOSITORY_HOSTS = { "github": "GitHub" }
LLM_MODELS = { "gemini-1.5-flash": "gemini-1.5-flash" }
REVIEWERS = { "simple-reviewer": "No additional context" }

st.set_page_config(page_title=TITLE, layout="wide")

def on_options_form_submit():
    try:
        repo = GitHubRepository(st.session_state.repository_url, st.session_state.repo_host_access_token)
        with st.spinner("Fetching pull requests..."):
            st.session_state.pull_requests = repo.get_pull_requests()
        st.session_state.repo = repo
        llm = ChatGoogleGenerativeAI(model=st.session_state.llm_model, google_api_key=st.session_state.llm_api_key)
        st.session_state.reviewer = SimpleReviewer(llm)
        st.session_state.review_section_available = True
    except Exception as e:
        st.error(f"Error getting repository details. Please check if the provided options are correct and try again.")
        with st.expander("Error details"):
            st.code(repr(e), language="python")
        st.session_state.review_section_available = False


if "review_section_available" not in st.session_state:
    st.session_state.review_section_available = False

if "show_initial_message" not in st.session_state:
    st.session_state.show_initial_message = True

if st.session_state.show_initial_message:
    st.info("Please provide details as required in the left sidebar.")
    st.session_state.show_initial_message = False

st.sidebar.title(TITLE)
st.sidebar.caption(SUB_TITLE)
st.sidebar.divider()
st.sidebar.subheader("Options")
with st.sidebar.form(key="options_form", enter_to_submit=False, border=False):
    # Repository details
    st.caption("Repository details")
    st.selectbox(
        label="Repository host*",
        options=REPOSITORY_HOSTS,
        key="repository_host",
        format_func=lambda option: REPOSITORY_HOSTS[option],
        help="The provider that hosts the git repository.")
    st.text_input(label="Access token (optional for public repositories)", type="password", key="repo_host_access_token")
    st.text_input(label="Repository URL*", key="repository_url", help="Https url for the repository.")

    # LLM details
    st.caption("LLM details")
    st.selectbox(
        label="Large language model*",
        options=LLM_MODELS,
        key="llm_model",
        format_func=lambda option: LLM_MODELS[option])
    st.text_input(label="API key (optional for free models)", type="password", key="llm_api_key")

    # Context options
    st.caption("Prompt options")
    st.selectbox(label="Additional context*",
                 options=REVIEWERS,
                 key="prompt_option",
                 format_func=lambda option: REVIEWERS[option])

    st.form_submit_button(label="Apply", type="primary", use_container_width=True, on_click=on_options_form_submit)

if st.session_state.review_section_available:
    st.selectbox(label="Pull request",
                   options=st.session_state.pull_requests,
                   key="pull_request",
                   placeholder="Select pull request",
                   format_func=lambda pr: f"#{pr.id}: {pr.title}")
    with st.expander(label="Pull request description"):
        st.write(st.session_state.pull_request.description, unsafe_allow_html=True)

    if st.button(label="Review", type="primary"):
        st.divider()
        try:
            if st.session_state.pull_request.changes is None:
                with st.spinner("Fetching pull request changes..."):
                    st.session_state.pull_request.changes = st.session_state.repo.get_pull_request_changes(st.session_state.pull_request)
            with st.spinner("Reviewing pull request..."):
                review_text = st.session_state.reviewer.review(st.session_state.pull_request)
                st.write(review_text, unsafe_allow_html=True)
        except Exception as ex:
            st.error(f"Error reviewing the pull request. Please check if the provided options are correct and try again.")
            with st.expander("Error details"):
                st.code(repr(ex), language="python")

