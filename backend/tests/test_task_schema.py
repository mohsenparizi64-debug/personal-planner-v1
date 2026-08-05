from app.schemas.task import TaskCreate


def test_task_create_accepts_empty_date_fields_as_none():
    payload = {
        "title": "تست",
        "description": "",
        "register_date": "2024-01-01",
        "duration_days": 3,
        "category": "work",
        "sub_goal_id": None,
        "goal_id": None,
        "last_action_date": "",
        "status": "not_started",
        "recurrence_type": "none",
        "recurrence_interval": 1,
        "recurrence_end_date": "",
        "priority": 0,
    }

    task = TaskCreate(**payload)

    assert task.last_action_date is None
    assert task.recurrence_end_date is None
