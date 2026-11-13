from pawpal_system import Pet, Task


def test_task_completion_marks_task_complete() -> None:
    task = Task("Walk", 20, "high")

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet("Mochi", "dog")
    task = Task("Walk", 20, "high")

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
