"""
utils/exceptions.py
--------------------
Custom exception classes used throughout the project.

Why custom exceptions instead of just raising generic Exception?
- They let calling code catch specific failure types (e.g. "the search
  API failed" vs. "the language model API failed") and respond
  appropriately, instead of blindly catching every possible error the
  exact same way.
- They make error messages in the terminal and in the Streamlit UI far
  easier to read and debug, because the exception's class name alone
  tells you which part of the system failed.
- This is a recognized software engineering best practice — popular
  libraries like `requests`, `openai`, and `google-generativeai` all
  define their own exception hierarchies for exactly this reason.
"""


class ResearchAgentError(Exception):
    """
    Base class for every custom exception raised by this project.

    Catching this single type (instead of listing every specific
    subclass) is useful in app.py, where we want to show *any*
    pipeline failure to the user as one friendly error message,
    without needing to know in advance every possible way it could fail.
    """
    pass


class TavilyAPIError(ResearchAgentError):
    """
    Raised when a call to the Tavily Search API fails.

    Typical causes: an invalid or missing API key, a network timeout,
    Tavily returning an error status code, or a response that's
    missing the data we expected.
    """
    pass


class  GroqAPIError(ResearchAgentError):
    """
    Raised when a call to the Gemini API fails.

    Typical causes: an invalid or missing API key, the request being
    blocked by Gemini's built-in safety filters, a network timeout,
    or Gemini returning an empty response.
    """
    pass


class AgentExecutionError(ResearchAgentError):
    """
    Raised when an agent fails to complete its task for a reason that
    is NOT a direct API failure — for example, if Gemini's response
    text can't be parsed into the structure the agent expected.

    Keeping this separate from TavilyAPIError and GeminiAPIError makes
    it immediately clear, while debugging, whether the problem came
    from the external API itself or from how this project processed
    that API's response.
    """
    pass
