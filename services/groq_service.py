# """
# services/openai_service.py
# ---------------------------
# A thin wrapper around OpenAI's API.

# Why wrap OpenAI inside our own service?

# - All AI-powered agents use the same generate() method.
# - Error handling exists in one place.
# - Model settings are controlled from config.py.
# - If we switch models later, only this file changes.
# """

# from openai import OpenAI

# from utils.exceptions import OpenAIAPIError
# from utils.logger import get_logger

# logger = get_logger(__name__)


# class OpenAIService:
#     """
#     Simple wrapper around OpenAI.

#     Parameters
#     ----------
#     api_key : str
#         OpenAI API key.
#     model_name : str
#         Model name (e.g. gpt-4o-mini).
#     temperature : float
#         Controls creativity.
#     max_tokens : int
#         Maximum response length.
#     """

#     def __init__(
#         self,
#         api_key: str,
#         model_name: str,
#         temperature: float = 0.4,
#         max_tokens: int = 1024,
#     ):
#         self._client = OpenAI(api_key=api_key)

#         self._model_name = model_name
#         self._temperature = temperature
#         self._max_tokens = max_tokens

#     def generate(self, prompt: str) -> str:
#         """
#         Send a prompt to OpenAI and return text.

#         Parameters
#         ----------
#         prompt : str
#             Prompt text.

#         Returns
#         -------
#         str
#             Generated response text.

#         Raises
#         ------
#         OpenAIAPIError
#             If OpenAI request fails.
#         """

#         logger.info(
#             f"Sending prompt to OpenAI ({len(prompt)} characters)"
#         )

#         try:
#             response = self._client.chat.completions.create(
#                 model=self._model_name,
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 temperature=self._temperature,
#                 max_tokens=self._max_tokens,
#             )

#         except Exception as exc:
#             raise OpenAIAPIError(
#                 f"OpenAI API call failed: {exc}"
#             ) from exc

#         text = (
#             response.choices[0]
#             .message.content
#             .strip()
#         )

#         if not text:
#             raise OpenAIAPIError(
#                 "OpenAI returned an empty response."
#             )

#         logger.info(
#             f"Received OpenAI response ({len(text)} characters)"
#         )

#         return text
"""
services/groq_service.py
------------------------
A thin wrapper around Groq's API.

Why wrap Groq inside our own service?

- All AI-powered agents use the same generate() method.
- Error handling exists in one place.
- Model settings are controlled from config.py.
- If we switch models later, only this file changes.
"""

from groq import Groq

from utils.exceptions import GroqAPIError
from utils.logger import get_logger

logger = get_logger(__name__)


class GroqService:
    """
    Simple wrapper around Groq.

    Parameters
    ----------
    api_key : str
        Groq API key.
    model_name : str
        Model name (e.g. llama-3.3-70b-versatile).
    temperature : float
        Controls creativity.
    max_tokens : int
        Maximum response length.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ):
        self._client = Groq(api_key=api_key)

        self._model_name = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        """
        Send a prompt to Groq and return text.
        """

        logger.info(
            f"Sending prompt to Groq ({len(prompt)} characters)"
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )

        except Exception as exc:
            print("REAL ERROR:", exc)
            raise

        text = (
            response.choices[0]
            .message.content
            .strip()
        )

        if not text:
            raise OpenAIAPIError(
                "Groq returned an empty response."
            )

        logger.info(
            f"Received Groq response ({len(text)} characters)"
        )

        return text