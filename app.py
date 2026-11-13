from datetime import date, time

import streamlit as st
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Owner, pet, and task objects are kept in Streamlit
session state so they remain available across app reruns and page navigation.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority, and recurrence)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    owner = Owner(
        name="Jordan",
        preferred_start_time=time(7, 30),
        available_minutes_per_day=90,
    )
    owner.add_pet(Pet(name="Mochi", species="dog"))
    st.session_state["owner"] = owner

owner: Owner = st.session_state["owner"]

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name, key="owner_name")
owner.name = owner_name

st.subheader("Pets")
with st.expander("Add a pet"):
    new_pet_name = st.text_input("New pet name", key="new_pet_name")
    new_pet_species = st.selectbox(
        "New pet species",
        ["dog", "cat", "other"],
        key="new_pet_species",
    )
    if st.button("Add pet"):
        if new_pet_name.strip():
            owner.add_pet(
                Pet(name=new_pet_name.strip(), species=new_pet_species)
            )
        else:
            st.error("Enter a pet name before adding it.")

if not owner.pets:
    st.info("Add a pet to start tracking care tasks.")
    st.stop()

pet_index = st.selectbox(
    "Select a pet",
    options=range(len(owner.pets)),
    format_func=lambda index: (
        f"{owner.pets[index].name} ({owner.pets[index].species})"
    ),
    key="selected_pet_index",
)
pet = owner.pets[pet_index]

st.markdown("### Tasks")
st.caption(f"Tasks are stored as Task objects on {pet.name}.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input(
        "Task title", value="Morning walk", key="task_title"
    )
with col2:
    duration = st.number_input(
        "Duration (minutes)",
        min_value=1,
        max_value=240,
        value=20,
        key="task_duration",
    )
with col3:
    priority = st.selectbox(
        "Priority", ["low", "medium", "high"], index=2, key="task_priority"
    )
with col4:
    recurrence = st.selectbox(
        "Recurrence", ["none", "daily", "weekly"], key="task_recurrence"
    )

due_date = None
if recurrence != "none":
    due_date = st.date_input(
        "First due date", value=date.today(), key="task_due_date"
    )

if st.button("Add task"):
    if task_title.strip():
        pet.add_task(
            Task(
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority,
                recurrence=recurrence,
                due_date=due_date,
            )
        )
    else:
        st.error("Enter a task title before adding it.")

tasks = pet.get_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "is_completed": task.is_completed,
                "recurrence": task.recurrence,
                "due_date": task.due_date,
            }
            for task in tasks
        ]
    )
    for task_index, task in enumerate(tasks):
        if not task.is_completed and st.button(
            f"Mark complete: {task.title}",
            key=f"complete_task_{pet_index}_{task_index}",
        ):
            next_task = pet.mark_task_complete(task)
            if next_task is not None:
                st.success(
                    f"Completed. The next occurrence is due "
                    f"{next_task.due_date:%B %d, %Y}."
                )
            else:
                st.success("Task marked complete.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Stored Session Objects")
st.write(f"Owner: {owner.name}")
st.write("Pets:", ", ".join(current_pet.name for current_pet in owner.pets))
st.write(f"Tasks across pets: {len(owner.get_all_tasks())}")
st.caption(
    "Owner, Pet, and Task instances are stored in session state. "
    "Adding a pet calls owner.add_pet(); adding a task calls pet.add_task()."
)
