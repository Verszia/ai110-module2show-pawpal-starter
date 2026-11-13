"""Core data models and scheduling interface for PawPal+."""

from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    """A care activity to schedule for a pet."""

    title: str
    duration_minutes: int
    priority: str
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def update_priority(self, priority: str) -> None:
        """Change this task's priority."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    care_tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """An owner, their scheduling preferences, and their pets."""

    name: str
    preferred_start_time: time
    available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's care."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Build and explain a daily plan from owner and pet care information."""

    start_time: time
    available_minutes: int
    plan: list[Task] = field(default_factory=list)

    def build_daily_plan(self, owner: Owner, pet: Pet) -> list[Task]:
        """Build a daily plan for one of the owner's pets."""
        raise NotImplementedError

    def select_tasks(
        self, tasks: list[Task], available_minutes: int
    ) -> list[Task]:
        """Select tasks that fit within the available time."""
        raise NotImplementedError

    def explain_plan(self, plan: list[Task]) -> str:
        """Explain why tasks were selected and ordered."""
        raise NotImplementedError