"""Review entity."""

from .base_model import BaseModel


class Review(BaseModel):
    """Represents a review written for a place."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text", "")
        self.rating = kwargs.get("rating", 0)
        self.user_id = kwargs.get("user_id")
        self.place_id = kwargs.get("place_id")

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text is required")
        self._text = cleaned

    @property
    def rating(self) -> int:
        return self._rating

    @rating.setter
    def rating(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("rating must be an integer")
        if value < 0 or value > 5:
            raise ValueError("rating must be between 0 and 5")
        self._rating = value

    @property
    def user_id(self) -> str:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("user_id must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("user_id is required")
        self._user_id = cleaned

    @property
    def place_id(self) -> str:
        return self._place_id

    @place_id.setter
    def place_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("place_id must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("place_id is required")
        self._place_id = cleaned

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "text": self.text,
                "rating": self.rating,
                "user_id": self.user_id,
                "place_id": self.place_id,
            }
        )
        return data
