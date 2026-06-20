import streamlit as st


def _init_state():
    if "role" not in st.session_state:
        st.session_state.role = "Client"
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1


def add_task(text: str):
    task = {"id": st.session_state.next_id, "text": text, "completed": False}
    st.session_state.next_id += 1
    st.session_state.tasks.append(task)


def toggle_task(task_id: int, completed: bool):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["completed"] = completed
            break


def switch_role():
    st.session_state.role = "Business" if st.session_state.role == "Client" else "Client"


_init_state()

st.set_page_config(page_title="Taskboard", layout="wide")
header_col, role_col = st.columns([4, 1])
with header_col:
    st.title("Taskboard — Business ↔ Client")
with role_col:
    st.markdown("### Current role")
    st.info(f"**{st.session_state.role}**")
    if st.button("Switch role", key="switch_role"):
        switch_role()

st.write("---")

if st.session_state.role == "Business":
    st.header("Business dashboard")
    if "new_task_text" not in st.session_state:
        st.session_state.new_task_text = ""

    def add_task_and_reset():
        add_task(st.session_state.new_task_text)
        st.session_state.new_task_text = ""

    with st.form("add_task_form", clear_on_submit=True):
        st.text_input("Task description", key="new_task_text")
        submitted = st.form_submit_button(
            "Add task",
            on_click=add_task_and_reset,
        )
        if submitted and st.session_state.new_task_text == "":
            st.success("Task added")

    open_tasks = [t for t in st.session_state.tasks if not t["completed"]]
    closed_tasks = [t for t in st.session_state.tasks if t["completed"]]

    if not st.session_state.tasks:
        st.info("No tasks yet")
    else:
        if open_tasks:
            st.subheader("Open tasks")
            for t in open_tasks:
                st.write(f"- {t['text']}")

        if closed_tasks:
            st.subheader("Completed tasks")
            for t in closed_tasks:
                st.markdown(f"- ~~{t['text']}~~")

else:
    st.header("Client view")
    open_tasks = [t for t in st.session_state.tasks if not t["completed"]]
    closed_tasks = [t for t in st.session_state.tasks if t["completed"]]

    if open_tasks:
        st.subheader("Open tasks")
        for t in open_tasks:
            st.checkbox(
                t["text"],
                key=f"task_{t['id']}",
                value=False,
                on_change=toggle_task,
                args=(t["id"], True),
            )

    if closed_tasks:
        st.subheader("Completed tasks")
        for t in closed_tasks:
            st.markdown(f"- ~~{t['text']}~~")

    if not open_tasks and not closed_tasks:
        st.info("No tasks yet")
