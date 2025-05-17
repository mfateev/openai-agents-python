import contextvars
import time
import uuid
from abc import ABC
from datetime import datetime
from random import Random
from typing import Any
from uuid import UUID

from agents import Agent, TContext, TResponseInputItem, RunHooks, RunConfig

from src.agents import Model, Runner

# Initialized to the DefaultRunInterceptor at the bottom of the file to avoid a circular import
_run_interceptor: contextvars.ContextVar["RunInterceptor"] = contextvars.ContextVar(
    "run_interceptor")


class RunInterceptor(ABC):
    """
    Intercepts parameters of Runner.run() as well as side effect calls like time, random, uuid4, etc.
    """

    @classmethod
    def get(cls) -> "RunInterceptor":
        return _run_interceptor.get()

    @classmethod
    def set_interceptor(cls, interceptor: "RunInterceptor") -> "contextvars.Token[RunInterceptor]":
        return _run_interceptor.set(interceptor)

    def intercept_run(self,
                      starting_agent: Agent[TContext],
                      input: str | list[TResponseInputItem],
                      context: TContext | None,
                      max_turns: int,
                      hooks: RunHooks[TContext] | None,
                      run_config: RunConfig | None,
                      previous_response_id: str | None) -> dict[str, Any]:
        return {
            starting_agent: starting_agent,
            input: input,
            context: context,
            max_turns: max_turns,
            hooks: hooks,
            run_config: run_config,
            previous_response_id: previous_response_id,
        }

    def get_model(self, agent: Agent[Any], run_config: RunConfig) -> Model | None:
        """
        Returns the current model.
        TODO:   Is this needed given that intercept_run.starting_agent contains the model field
                as well as run_config.model and run_config.model_provider?
        """
        pass

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


class DefaultRunInterceptor(RunInterceptor):
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

    def get_model(self, agent: Agent[Any], run_config: RunConfig) -> Model | None:
        return None

    def patched(self, id: str) -> bool:
        return True

    def deprecate_patch(id: str) -> None:
        return

    def intercept_agent(self, agent: Agent) -> Agent:
        return agent


def _safe_random() -> Random:
    return RunInterceptor.get().random()


def _safe_time(tz=None) -> float:
    return RunInterceptor.get().time(tz)


def _safe_time_ns() -> int:
    return RunInterceptor.get().time_ns()


def _safe_uuid4() -> UUID:
    return RunInterceptor.get().uuid4()


def _patched(id: str) -> bool:
    return RunInterceptor.get().patched(id)


def _deprecate_patch(id: str) -> None:
    RunInterceptor.get().deprecate_patch(id)


_run_interceptor.set(DefaultRunInterceptor())
