"""V1 API namespace exports."""

from .amenities import api as amenities_ns
from .auth import api as auth_ns
from .places import api as places_ns
from .reviews import api as reviews_ns
from .status import api as status_ns
from .users import api as users_ns

__all__ = ["status_ns", "users_ns", "places_ns", "reviews_ns", "amenities_ns", "auth_ns"]
