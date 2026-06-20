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

st.title("Taskboard — Business ↔ Client")

cols = st.columns([1, 1, 1])
with cols[2]:
    st.markdown(f"**Role:** {st.session_state.role}")
    if st.button("Switch role"):
        switch_role()

st.write("---")

if st.session_state.role == "Business":
    st.header("Business dashboard")
    with st.form("add_task_form", clear_on_submit=True):
        text = st.text_input("Task description")
        submitted = st.form_submit_button("Add task")
        if submitted and text:
            add_task(text)
            st.success("Task added")

    st.subheader("All tasks")
    if not st.session_state.tasks:
        st.info("No tasks yet")
    else:
        for t in st.session_state.tasks:
            status = "✅" if t["completed"] else "🟡 Open"
            st.write(f"- {t['text']} ({status})")

else:
    st.header("Client view — Open tasks")
    open_tasks = [t for t in st.session_state.tasks if not t["completed"]]
    if not open_tasks:
        st.info("No open tasks — you're all caught up!")
    else:
        for t in open_tasks:
            checked = st.checkbox(t["text"], key=f"task_{t['id']}")
            if checked:
                toggle_task(t["id"], True)
                st.experimental_rerun()

    completed = [t for t in st.session_state.tasks if t["completed"]]
    if completed:
        st.subheader("Completed")
        for t in completed:
            st.write(f"- {t['text']}")

