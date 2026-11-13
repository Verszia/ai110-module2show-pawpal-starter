from datetime import date, datetime, time, timedelta

from pawpal_system import Owner, Pet, ScheduledTask, Scheduler, Task


def test_task_completion_marks_task_complete() -> None:
    task = Task("Walk", 20, "high")

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet("Mochi", "dog")
    task = Task("Walk", 20, "high")

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1


def test_scheduler_sorts_tasks_by_due_time_without_mutating_input() -> None:
    later = Task("Walk", 20, "high", due_by=time(9, 0))
    untimed = Task("Play", 15, "medium")
    earlier = Task("Breakfast", 10, "high", due_by=time(8, 0))
    tasks = [later, untimed, earlier]

    sorted_tasks = Scheduler().sort_by_time(tasks)

    assert sorted_tasks == [earlier, later, untimed]
    assert tasks == [later, untimed, earlier]


def test_scheduler_filters_tasks_by_completion_and_pet_name() -> None:
    owner = Owner("Jordan", time(7, 30), 90)
    dog = Pet("Mochi", "dog")
    cat = Pet("Nori", "cat")
    pending_dog_task = Task("Walk", 20, "high")
    completed_dog_task = Task("Breakfast", 10, "high", is_completed=True)
    pending_cat_task = Task("Feeding", 10, "high")
    dog.add_task(pending_dog_task)
    dog.add_task(completed_dog_task)
    cat.add_task(pending_cat_task)
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler()

    assert scheduler.filter_tasks(
        owner, is_completed=False, pet_name="mochi"
    ) == [pending_dog_task]
    assert scheduler.filter_tasks(owner, is_completed=True) == [completed_dog_task]


def test_completing_daily_task_adds_next_occurrence() -> None:
    pet = Pet("Mochi", "dog")
    task = Task(
        "Medication",
        5,
        "high",
        due_by=time(8, 0),
        recurrence="daily",
        due_date=date(2026, 11, 13),
    )
    pet.add_task(task)

    next_task = pet.mark_task_complete(task, completed_on=date(2026, 11, 13))

    assert task.is_completed is True
    assert next_task is not None
    assert next_task is not task
    assert next_task.due_date == date(2026, 11, 14)
    assert next_task.recurrence == "daily"
    assert next_task.due_by == time(8, 0)
    assert pet.get_tasks() == [task, next_task]


def test_completing_weekly_task_adds_occurrence_seven_days_later() -> None:
    pet = Pet("Mochi", "dog")
    task = Task("Grooming", 30, "medium", recurrence="weekly")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task, completed_on=date(2026, 11, 13))

    assert next_task is not None
    assert next_task.due_date == date(2026, 11, 13) + timedelta(days=7)
    assert next_task.recurrence == "weekly"
    assert pet.get_tasks() == [task, next_task]


def test_completing_recurring_task_twice_does_not_duplicate_occurrence() -> None:
    pet = Pet("Mochi", "dog")
    task = Task("Walk", 20, "high", recurrence="daily")
    pet.add_task(task)

    pet.mark_task_complete(task, completed_on=date(2026, 11, 13))
    duplicate = pet.mark_task_complete(task, completed_on=date(2026, 11, 13))

    assert duplicate is None
    assert len(pet.get_tasks()) == 2


def test_scheduler_does_not_schedule_future_recurring_occurrence() -> None:
    owner = Owner("Jordan", time(7, 30), 90)
    pet = Pet("Mochi", "dog")
    pet.add_task(
        Task("Medication", 5, "high", recurrence="daily", due_date=date(2026, 11, 14))
    )
    owner.add_pet(pet)

    plan = Scheduler().build_daily_plan(owner, date(2026, 11, 13))

    assert plan == []


def test_scheduler_detects_overlapping_tasks_and_ignores_adjacent_tasks() -> None:
    start = datetime(2026, 11, 13, 8, 0)
    walk = Task("Walk", 30, "high")
    feeding = Task("Feeding", 10, "high")
    playtime = Task("Playtime", 15, "medium")
    plan = [
        ScheduledTask(walk, start, start + timedelta(minutes=30)),
        ScheduledTask(feeding, start, start + timedelta(minutes=10)),
        ScheduledTask(
            playtime,
            start + timedelta(minutes=30),
            start + timedelta(minutes=45),
        ),
    ]

    warnings = Scheduler().detect_conflicts(plan)

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]
    assert "08:00 AM" in warnings[0]
    assert "08:10 AM" in warnings[0]


def test_scheduler_returns_no_conflicts_for_sequential_tasks() -> None:
    start = datetime(2026, 11, 13, 8, 0)
    first = Task("Walk", 20, "high")
    second = Task("Feeding", 10, "high")
    plan = [
        ScheduledTask(first, start, start + timedelta(minutes=20)),
        ScheduledTask(
            second,
            start + timedelta(minutes=20),
            start + timedelta(minutes=30),
        ),
    ]

    assert Scheduler().detect_conflicts(plan) == []
