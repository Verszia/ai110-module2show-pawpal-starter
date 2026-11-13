"""Core data models and scheduling interface for PawPal+."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Literal

Priority = Literal["high", "medium", "low"]
_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A care activity to schedule for a pet."""

    title: str
    duration_minutes: int
    priority: Priority
    is_completed: bool = False
    due_by: time | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title cannot be empty")
        if (
            not isinstance(self.duration_minutes, int)
            or isinstance(self.duration_minutes, bool)
            or self.duration_minutes <= 0
        ):
            raise ValueError("duration_minutes must be a positive integer")
        if not isinstance(self.priority, str) or self.priority not in _PRIORITY_ORDER:
            raise ValueError("priority must be high, medium, or low")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def update_priority(self, priority: Priority) -> None:
        """Change this task's priority."""
        if not isinstance(priority, str) or priority not in _PRIORITY_ORDER:
            raise ValueError("priority must be high, medium, or low")
        self.priority = priority


@dataclass(frozen=True)
class ScheduledTask:
    """A task assigned a concrete time in a daily plan."""

    task: Task
    starts_at: datetime
    ends_at: datetime


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    care_tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name cannot be empty")
        if not isinstance(self.species, str) or not self.species.strip():
            raise ValueError("species cannot be empty")

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        if not any(existing is task for existing in self.care_tasks):
            self.care_tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        for index, existing in enumerate(self.care_tasks):
            if existing is task:
                del self.care_tasks[index]
                return
        raise ValueError("task does not belong to this pet")

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        return list(self.care_tasks)


@dataclass
class Owner:
    """An owner, their scheduling preferences, and their pets."""

    name: str
    preferred_start_time: time
    available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name cannot be empty")
        if (
            not isinstance(self.available_minutes_per_day, int)
            or isinstance(self.available_minutes_per_day, bool)
            or self.available_minutes_per_day < 0
        ):
            raise ValueError(
                "available_minutes_per_day must be a non-negative integer"
            )
        if not isinstance(self.preferred_start_time, time):
            raise ValueError("preferred_start_time must be a time")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        if not any(existing is pet for existing in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's care."""
        for index, existing in enumerate(self.pets):
            if existing is pet:
                del self.pets[index]
                return
        raise ValueError("pet does not belong to this owner")

    def get_all_tasks(self) -> list[Task]:
        """Return each task belonging to this owner's pets once."""
        tasks: list[Task] = []
        seen_task_ids: set[int] = set()
        for pet in self.pets:
            for task in pet.get_tasks():
                if id(task) not in seen_task_ids:
                    tasks.append(task)
                    seen_task_ids.add(id(task))
        return tasks


@dataclass
class Scheduler:
    """Build owner-wide plans that honor time, priority, and deadline constraints."""

    plan: list[ScheduledTask] = field(default_factory=list)

    def build_daily_plan(
        self, owner: Owner, schedule_date: date
    ) -> list[ScheduledTask]:
        """Schedule tasks from all pets using the owner's sole time budget."""
        self.plan = self._select_tasks(owner.get_all_tasks(), owner, schedule_date)
        return list(self.plan)

    def _select_tasks(
        self, tasks: list[Task], owner: Owner, schedule_date: date
    ) -> list[ScheduledTask]:
        """Rank by priority, then deadline and duration; skip infeasible tasks and continue."""
        ordered_tasks = sorted(
            tasks,
            key=lambda task: (
                _PRIORITY_ORDER[task.priority],
                task.due_by or time.max,
                task.duration_minutes,
            ),
        )
        day_start = datetime.combine(schedule_date, owner.preferred_start_time)
        scheduled: list[ScheduledTask] = []
        elapsed_minutes = 0

        for task in ordered_tasks:
            starts_at = day_start + timedelta(minutes=elapsed_minutes)
            if not self._can_schedule(task, owner, starts_at, elapsed_minutes):
                continue
            ends_at = starts_at + timedelta(minutes=task.duration_minutes)
            scheduled.append(ScheduledTask(task, starts_at, ends_at))
            elapsed_minutes += task.duration_minutes

        return scheduled

    def _can_schedule(
        self,
        task: Task,
        owner: Owner,
        starts_at: datetime,
        elapsed_minutes: int,
    ) -> bool:
        """Check completion, owner time budget, same-day fit, and deadline."""
        if task.is_completed:
            return False
        if elapsed_minutes + task.duration_minutes > owner.available_minutes_per_day:
            return False

        ends_at = starts_at + timedelta(minutes=task.duration_minutes)
        if ends_at.date() != starts_at.date():
            return False
        if task.due_by is not None and ends_at.time() > task.due_by:
            return False
        return True

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Explain why tasks were selected and ordered."""
        if not plan:
            return "No incomplete tasks fit the owner's time and deadline constraints."

        return "\n".join(
            f"{item.starts_at:%H:%M}-{item.ends_at:%H:%M} - "
            f"{item.task.title} ({item.task.duration_minutes} min, "
            f"priority: {item.task.priority}; selected by priority and feasibility)"
            for item in plan
        )
