from typing import Any, Dict, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from accqsure import AccQsure


class Text(object):
    """Manager for text processing operations.

    Provides methods for text generation, vectorization, and tokenization
    using the AccQsure LLM services. Maps to the /v1/text API endpoints.
    """

    def __init__(self, accqsure: "AccQsure") -> None:
        """Initialize the Text manager.

        Args:
            accqsure: The AccQsure client instance.
        """
        self.accqsure = accqsure

    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.8,
        **kwargs: Any,
    ) -> str:
        """Generate text using the LLM service.

        Generates text based on a conversation history using streaming
        response. The method accumulates the generated text from the
        streaming response.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
                     keys. Roles can be 'system', 'user', or 'assistant'.
            max_tokens: Maximum number of tokens to generate. Defaults to 2048.
            temperature: Sampling temperature (0.0 to 1.0). Higher values make
                       output more random. Defaults to 0.8.
            **kwargs: Additional generation parameters (e.g., seed, stop sequences).

        Returns:
            Generated text as a string.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query_stream(
            "/text/generate",
            "POST",
            None,
            {
                **kwargs,
                **dict(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                ),
            },
        )
        return resp

    async def vectorize(
        self, inputs: Union[str, List[str]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Convert text inputs to vector embeddings.

        Generates vector embeddings for the provided text inputs using
        the embedding model.

        Args:
            inputs: Single string or list of strings to vectorize.
            **kwargs: Additional parameters for vectorization.

        Returns:
            Dictionary containing the vector embeddings.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            "/text/vectorize", "POST", None, {**kwargs, **dict(inputs=inputs)}
        )
        return resp

    async def tokenize(
        self, inputs: Union[str, List[str]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Tokenize text inputs.

        Converts text inputs into tokens using the tokenizer for the
        configured LLM model.

        Args:
            inputs: Single string or list of strings to tokenize.
            **kwargs: Additional parameters for tokenization.

        Returns:
            Dictionary containing the tokenization results.

        Raises:
            ApiError: If the API returns an error.
            AccQsureException: If there's an error making the request.
        """
        resp = await self.accqsure._query(
            "/text/tokenize", "POST", None, {**kwargs, **dict(inputs=inputs)}
        )
        return resp
