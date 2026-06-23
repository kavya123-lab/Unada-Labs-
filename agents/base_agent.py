"""
agents/base_agent.py
---------------------
Defines BaseAgent: the abstract base class every agent in this
project inherits from.

Why use an abstract base class here?
- It guarantees every agent exposes the exact same interface: a
  run(context) method that takes a ResearchContext and returns one.
  The orchestrator can then call every agent the same way, in a
  simple loop, with no special-case logic per agent.
- It's the Template Method design pattern: the *shape* of "an agent"
  is defined once here, while *what each agent actually does* is
  defined individually in each subclass.
- It catches a real category of bugs early: if you write a new agent
  and forget to implement run(), Python refuses to let you even
  create an instance of that class — rather than failing later with a
  confusing AttributeError when the orchestrator tries to call it.
"""

from abc import ABC, abstractmethod

from core.context import ResearchContext
from utils.logger import get_logger


class BaseAgent(ABC):
    """
    Abstract base class for every agent in the pipeline.

    Subclasses must implement run(context), which should:
    1. Read whatever fields it needs from the given ResearchContext.
    2. Do its work (call a service, build a prompt, parse a result).
    3. Write its result into the appropriate ResearchContext field(s).
    4. Return the same context object.

    Every subclass also automatically gets a ready-to-use
    `self.logger`, named after the subclass itself, so log output is
    always clearly labeled with which agent produced it.
    """

    def __init__(self):
        # self.__class__.__name__ gives the name of whichever subclass
        # is actually being created (e.g. "ResearchAgent"), not
        # "BaseAgent" — so log messages are always attributed to the
        # correct agent, automatically, with no extra effort per agent.
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def run(self, context: ResearchContext) -> ResearchContext:
        """
        Execute this agent's task and return the updated context.

        Parameters
        ----------
        context : ResearchContext
            The shared pipeline state, possibly already containing
            results written by earlier agents.

        Returns
        -------
        ResearchContext
            The same context object, with this agent's result(s)
            added to it.
        """
        raise NotImplementedError
