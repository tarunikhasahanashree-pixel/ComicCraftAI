
class ComicCraftError(Exception):
    """Base exception for ComicCraft application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GeminiAPIError(ComicCraftError):
    """Raised when Gemini API requests fail."""


class ImageGenerationError(ComicCraftError):
    """Raised when comic panel image generation fails."""


class StoryGenerationError(ComicCraftError):
    """Raised when story generation fails."""
