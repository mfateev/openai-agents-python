import contextvars
import time
import uuid
from abc import ABC
from datetime import datetime
from operator import truediv
from random import Random
from uuid import UUID

from src.agents import Model

_side_effects_interceptor: contextvars.ContextVar["SideEffectsInterceptor"] = contextvars.ContextVar(
    "side_effects_interceptor", default=DefaultSideEffectsInterceptor()
)


class SideEffectsInterceptor(ABC):
    """
    Intercepts side effects in the agent's actions.
    """

    @classmethod
    def get(cls) -> "SideEffectsInterceptor":
        return _side_effects_interceptor.get()

    @classmethod
    def set_interceptor(cls, interceptor: "SideEffectsInterceptor") -> "contextvars.Token[SideEffectsInterceptor]":
        return _side_effects_interceptor.set(interceptor)

    def random(self) -> Random:
        pass

    def time(self, tz=None) -> float:
        """
        Returns the current time.
        """
        pass

    def time_ns(self) -> int:
        """
        Returns the current time.
        """
        pass

    def now(self, tz=None) -> datetime:
        """
        Returns the current time.
        """
        return datetime.fromtimestamp(self.time(), tz=tz)

    def uuid4(self) -> UUID:
        """
        Returns a random UUID4.
        """
        pass

    def get_model(self, model: str) -> Model | None:
        """
        Returns the current model.
        """
        pass

    def patched(self, id: str) -> bool:
        """
        Supports backward compatible changes to durable execution.

        When called, this will only return true if code should take the newer path
        which means this is either not replaying or is replaying and has seen this
        patch before.

        Use :py:func:`deprecate_patch` when all workflows are done and will never be
        queried again. The old code path can be used at that time too.

        Args:
            id: The identifier for this patch. This identifier may be used
                repeatedly in the same workflow to represent the same patch

        Returns:
            True if this should take the newer path, false if it should take the
            older path.
        """
        pass

    def deprecate_patch(id: str) -> None:
        """Mark a patch as deprecated.

        This marks code path that had :py:func:`patched` in a previous version of
        the code as no longer applicable because all durable executions that use the old code
        path are done and will never be queried again. Therefore the old code path
        is removed as well.

        Args:
            id: The identifier originally used with :py:func:`patched`.
        """
        pass


class _DefaultSideEffectsInterceptor(SideEffectsInterceptor):
    """
    Default implementation of SideEffectsInterceptor.
    """

    def random(self) -> Random:
        return Random()

    def time(self, tz=None) -> float:
        return datetime.now(tz).timestamp() if tz else datetime.now().timestamp()

    def time_ns(self) -> int:
        return time.time_ns()

    def uuid4(self) -> UUID:
        return uuid.uuid4()

    def get_model(self, model: str) -> Model | None:
        return None

    def patched(self, id: str) -> bool:
        return True

    def deprecate_patch(id: str) -> None:
        return


def _safe_random() -> Random:
    return SideEffectsInterceptor.get().random()


def _safe_time(tz=None) -> float:
    return SideEffectsInterceptor.get().time(tz)


def _safe_time_ns() -> int:
    return SideEffectsInterceptor.get().time_ns()


def _safe_uuid4() -> UUID:
    return SideEffectsInterceptor.get().uuid4()


def _patched(id: str) -> bool:
    return SideEffectsInterceptor.get().patched(id)


def _deprecate_patch(id: str) -> None:
    SideEffectsInterceptor.get().deprecate_patch(id)
