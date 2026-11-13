from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    today = date.today()

    owner = Owner(
        name="Jordan",
        preferred_start_time=time(7, 30),
        available_minutes_per_day=90,
    )
    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Nori", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("Morning walk", 30, "high", due_by=time(9, 0)))
    dog.add_task(Task("Breakfast", 10, "high", due_by=time(8, 15)))
    cat.add_task(Task("Feeding", 10, "high", due_by=time(8, 30)))
    cat.add_task(Task("Playtime", 20, "medium"))

    scheduler = Scheduler()
    plan = scheduler.build_daily_plan(owner, today)
    pet_names_by_task = {
        id(task): pet.name for pet in owner.pets for task in pet.get_tasks()
    }

    print(f"Today's Schedule - {today:%A, %B %d, %Y}")
    if not plan:
        print("No tasks fit the owner's time and deadline constraints.")
        return

    for item in plan:
        print(
            f"{item.starts_at:%I:%M %p}-{item.ends_at:%I:%M %p} | "
            f"{pet_names_by_task[id(item.task)]} - {item.task.title} "
            f"({item.task.duration_minutes} min, "
            f"priority: {item.task.priority})"
        )


if __name__ == "__main__":
    main()