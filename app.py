from __future__ import annotations

from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


def _pet_names_by_task(owner: Owner) -> dict[int, list[str]]:
    names: dict[int, list[str]] = {}
    for pet in owner.pets:
        for task in pet.get_tasks():
            names.setdefault(id(task), []).append(pet.name)
    return names


def _remove_selected_pet(owner: Owner) -> None:
    index = st.session_state.get("selected_pet_index", 0)
    if isinstance(index, int) and 0 <= index < len(owner.pets):
        pet_name = owner.pets[index].name
        owner.remove_pet(owner.pets[index])
        st.session_state["selected_pet_index"] = 0
        st.session_state["notice"] = f"Removed {pet_name}."


def _task_row(task: Task, pet_names: list[str]) -> dict[str, str | int]:
    return {
        "Pet": ", ".join(pet_names),
        "Task": task.title,
        "Duration (min)": task.duration_minutes,
        "Priority": task.priority.title(),
        "Status": "Completed" if task.is_completed else "Incomplete",
        "Due by": task.due_by.strftime("%I:%M %p") if task.due_by else "—",
        "Due date": task.due_date.strftime("%b %d, %Y") if task.due_date else "—",
        "Recurrence": task.recurrence.title(),
    }


if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(
        name="Owner",
        preferred_start_time=time(7, 30),
        available_minutes_per_day=90,
    )

owner: Owner = st.session_state["owner"]
scheduler = Scheduler()

st.title("🐾 PawPal+")
st.caption("Plan and track care routines for every pet in your household.")

notice = st.session_state.pop("notice", None)
if notice:
    st.success(notice)

with st.sidebar:
    st.header("Owner settings")
    owner_name = st.text_input(
        "Owner name",
        value="",
        placeholder="Enter owner name",
        key="owner_name",
    )
    if owner_name.strip():
        owner.name = owner_name.strip()
    else:
        st.info("Add an owner name when you're ready.")

    owner.preferred_start_time = st.time_input(
        "Preferred start time",
        value=owner.preferred_start_time,
        key="preferred_start_time",
    )
    owner.available_minutes_per_day = st.number_input(
        "Available minutes per day",
        min_value=0,
        max_value=1440,
        value=owner.available_minutes_per_day,
        step=15,
        key="available_minutes_per_day",
    )

    st.divider()
    st.header("Pets")
    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("Pet name")
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
        add_pet = st.form_submit_button("Add pet")
    if add_pet:
        if new_pet_name.strip():
            owner.add_pet(Pet(new_pet_name.strip(), new_pet_species))
            st.session_state["notice"] = f"Added {new_pet_name.strip()}."
            st.rerun()
        else:
            st.error("Enter a pet name before adding it.")

    if owner.pets:
        if (
            "selected_pet_index" not in st.session_state
            or st.session_state["selected_pet_index"] >= len(owner.pets)
        ):
            st.session_state["selected_pet_index"] = 0
        st.selectbox(
            "Manage pet",
            options=range(len(owner.pets)),
            format_func=lambda index: (
                f"{owner.pets[index].name} ({owner.pets[index].species})"
            ),
            key="selected_pet_index",
        )
        st.button(
            "Remove selected pet",
            on_click=_remove_selected_pet,
            args=(owner,),
            help="This also removes the pet's tasks from the household plan.",
        )
    else:
        st.info("Add a pet to start tracking care tasks.")

task_tab, schedule_tab, overview_tab = st.tabs(
    ["Tasks", "Daily schedule", "Household overview"]
)

with task_tab:
    st.subheader("Care tasks")
    if owner.pets:
        selected_pet = owner.pets[st.session_state["selected_pet_index"]]
        st.caption(f"Add a care task for **{selected_pet.name}**.")

        title_col, duration_col, priority_col, recurrence_col = st.columns(4)
        with title_col:
            task_title = st.text_input("Task title", key="task_title")
        with duration_col:
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=1440,
                value=20,
                key="task_duration",
            )
        with priority_col:
            priority = st.selectbox(
                "Priority",
                ["high", "medium", "low"],
                key="task_priority",
            )
        with recurrence_col:
            recurrence = st.selectbox(
                "Recurrence",
                ["none", "daily", "weekly"],
                key="task_recurrence",
            )

        deadline_col, due_date_col = st.columns(2)
        with deadline_col:
            has_deadline = st.checkbox("Set a time deadline", key="has_task_deadline")
            due_by = (
                st.time_input("Must finish by", value=time(8, 0), key="task_due_by")
                if has_deadline
                else None
            )
        with due_date_col:
            has_due_date = recurrence != "none" or st.checkbox(
                "Set a due date", key="has_task_due_date"
            )
            due_date = (
                st.date_input("Due date", value=date.today(), key="task_due_date")
                if has_due_date
                else None
            )

        if st.button("Add task", type="primary"):
            if not task_title.strip():
                st.error("Enter a task title before adding it.")
            else:
                selected_pet.add_task(
                    Task(
                        title=task_title.strip(),
                        duration_minutes=int(duration),
                        priority=priority,
                        due_by=due_by,
                        recurrence=recurrence,
                        due_date=due_date,
                    )
                )
                st.success(f"Added {task_title.strip()} for {selected_pet.name}.")

    st.divider()
    st.markdown("#### Household task list")
    filter_col, pet_filter_col = st.columns(2)
    with filter_col:
        status_label = st.selectbox(
            "Completion status",
            ["All tasks", "Incomplete", "Completed"],
            key="task_status_filter",
        )
    with pet_filter_col:
        pet_filter = st.selectbox(
            "Pet",
            ["All pets"] + list(dict.fromkeys(pet.name for pet in owner.pets)),
            key="task_pet_filter",
        )

    status_filter = {
        "All tasks": None,
        "Incomplete": False,
        "Completed": True,
    }[status_label]
    filtered_tasks = scheduler.filter_tasks(
        owner,
        is_completed=status_filter,
        pet_name=None if pet_filter == "All pets" else pet_filter,
    )
    sorted_tasks = scheduler.sort_by_time(filtered_tasks)
    pet_names = _pet_names_by_task(owner)

    if sorted_tasks:
        st.table([_task_row(task, pet_names[id(task)]) for task in sorted_tasks])
        st.caption(
            "Tasks are ordered by deadline; tasks without a deadline appear last."
        )
        for task in sorted_tasks:
            with st.expander(f"Edit {task.title}", expanded=False):
                edit_title = st.text_input(
                    "Task title",
                    value=task.title,
                    key=f"edit_title_{id(task)}",
                )
                edit_duration = st.number_input(
                    "Duration (minutes)",
                    min_value=1,
                    max_value=1440,
                    value=task.duration_minutes,
                    key=f"edit_duration_{id(task)}",
                )
                edit_priority = st.selectbox(
                    "Priority",
                    ["high", "medium", "low"],
                    index=["high", "medium", "low"].index(task.priority),
                    key=f"edit_priority_{id(task)}",
                )
                edit_recurrence = st.selectbox(
                    "Recurrence",
                    ["none", "daily", "weekly"],
                    index=["none", "daily", "weekly"].index(task.recurrence),
                    key=f"edit_recurrence_{id(task)}",
                )
                edit_has_deadline = st.checkbox(
                    "Set a time deadline",
                    value=task.due_by is not None,
                    key=f"edit_has_deadline_{id(task)}",
                )
                edit_due_by = (
                    st.time_input(
                        "Must finish by",
                        value=task.due_by or time(8, 0),
                        key=f"edit_due_by_{id(task)}",
                    )
                    if edit_has_deadline
                    else None
                )
                edit_has_due_date = st.checkbox(
                    "Set a due date",
                    value=task.due_date is not None,
                    key=f"edit_has_due_date_{id(task)}",
                )
                edit_due_date = (
                    st.date_input(
                        "Due date",
                        value=task.due_date or date.today(),
                        key=f"edit_due_date_{id(task)}",
                    )
                    if edit_has_due_date
                    else None
                )
                if st.button("Save changes", key=f"save_task_{id(task)}"):
                    try:
                        updated_task = Task(
                            title=edit_title.strip(),
                            duration_minutes=int(edit_duration),
                            priority=edit_priority,
                            due_by=edit_due_by,
                            recurrence=edit_recurrence,
                            due_date=edit_due_date,
                        )
                    except ValueError as error:
                        st.error(str(error))
                    else:
                        task.title = updated_task.title
                        task.duration_minutes = updated_task.duration_minutes
                        task.update_priority(updated_task.priority)
                        task.due_by = updated_task.due_by
                        task.recurrence = updated_task.recurrence
                        task.due_date = updated_task.due_date
                        st.session_state["notice"] = f"Updated {task.title}."
                        st.rerun()

            action_col, remove_col = st.columns([1, 1])
            if not task.is_completed:
                with action_col:
                    if st.button(
                        f"Complete: {task.title}",
                        key=f"complete_task_{id(task)}",
                    ):
                        task_pet = next(
                            pet
                            for pet in owner.pets
                            if any(existing is task for existing in pet.get_tasks())
                        )
                        next_task = task_pet.mark_task_complete(task)
                        if next_task is not None:
                            st.session_state["notice"] = (
                                f"Completed {task.title}. The next occurrence is due "
                                f"{next_task.due_date:%B %d, %Y}."
                            )
                        else:
                            st.session_state["notice"] = f"Completed {task.title}."
                        st.rerun()
            with remove_col:
                if st.button(f"Remove: {task.title}", key=f"remove_task_{id(task)}"):
                    for pet in owner.pets:
                        if any(existing is task for existing in pet.get_tasks()):
                            pet.remove_task(task)
                    st.session_state["notice"] = f"Removed {task.title}."
                    st.rerun()
    else:
        st.info("No tasks match these filters.")

with schedule_tab:
    st.subheader("Daily care plan")
    schedule_date = st.date_input(
        "Plan date",
        value=date.today(),
        key="schedule_date",
    )
    plan = scheduler.build_daily_plan(owner, schedule_date)
    planned_minutes = sum(item.task.duration_minutes for item in plan)
    metric_cols = st.columns(3)
    metric_cols[0].metric("Scheduled tasks", len(plan))
    metric_cols[1].metric(
        "Planned time",
        f"{planned_minutes} min",
    )
    metric_cols[2].metric(
        "Daily availability",
        f"{owner.available_minutes_per_day} min",
    )

    if plan:
        pet_names = _pet_names_by_task(owner)
        st.table(
            [
                {
                    "Start": item.starts_at.strftime("%I:%M %p"),
                    "End": item.ends_at.strftime("%I:%M %p"),
                    "Pet": ", ".join(pet_names[id(item.task)]),
                    "Task": item.task.title,
                    "Duration (min)": item.task.duration_minutes,
                    "Priority": item.task.priority.title(),
                    "Due by": (
                        item.task.due_by.strftime("%I:%M %p")
                        if item.task.due_by
                        else "—"
                    ),
                    "Due date": (
                        item.task.due_date.strftime("%b %d, %Y")
                        if item.task.due_date
                        else "—"
                    ),
                    "Recurrence": item.task.recurrence.title(),
                }
                for item in plan
            ]
        )
        st.markdown("#### Why these tasks?")
        st.info(scheduler.explain_plan(plan))
    else:
        st.info(scheduler.explain_plan(plan))

    conflicts = scheduler.detect_conflicts(plan)
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No overlapping tasks in this plan.")

    incomplete_due_tasks = [
        task
        for task in owner.get_all_tasks()
        if not task.is_completed
        and (task.due_date is None or task.due_date <= schedule_date)
    ]
    scheduled_task_ids = {id(item.task) for item in plan}
    unscheduled = scheduler.sort_by_time(
        [
            task
            for task in incomplete_due_tasks
            if id(task) not in scheduled_task_ids
        ]
    )
    if unscheduled:
        st.warning(
            "Some incomplete tasks due by this date did not fit the daily "
            "time, deadline, or same-day constraints."
        )
        st.table(
            [
                _task_row(task, _pet_names_by_task(owner)[id(task)])
                for task in unscheduled
            ]
        )

    upcoming = [
        task
        for task in owner.get_all_tasks()
        if not task.is_completed
        and task.due_date is not None
        and task.due_date > schedule_date
    ]
    if upcoming:
        st.markdown("#### Upcoming tasks")
        st.table(
            [
                _task_row(task, _pet_names_by_task(owner)[id(task)])
                for task in sorted(upcoming, key=lambda task: task.due_date)
            ]
        )

with overview_tab:
    st.subheader("Household overview")
    info_cols = st.columns(3)
    info_cols[0].metric("Owner", owner_name.strip() or "Not set")
    info_cols[1].metric(
        "Preferred start",
        owner.preferred_start_time.strftime("%I:%M %p"),
    )
    info_cols[2].metric("Daily availability", f"{owner.available_minutes_per_day} min")

    if owner.pets:
        st.table(
            [
                {
                    "Pet": pet.name,
                    "Species": pet.species.title(),
                    "Total tasks": len(pet.get_tasks()),
                    "Incomplete tasks": sum(
                        not task.is_completed for task in pet.get_tasks()
                    ),
                }
                for pet in owner.pets
            ]
        )
    else:
        st.info("No pets have been added yet.")

    all_tasks = owner.get_all_tasks()
    st.caption(
        f"{len(all_tasks)} unique task(s) across {len(owner.pets)} pet(s). "
        "Recurring tasks create their next occurrence when marked complete."
    )
