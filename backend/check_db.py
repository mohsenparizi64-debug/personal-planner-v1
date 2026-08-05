import asyncio
from app.db.session import AsyncSessionLocal
from app.models.all_models import Task, User
from sqlalchemy import select, func

async def check_db():
    async with AsyncSessionLocal() as db:
        # Check users
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"  - {user.email} (ID: {user.id})")
        
        # Check tasks
        tasks_result = await db.execute(select(func.count(Task.id)))
        task_count = tasks_result.scalar()
        print(f"\nTotal tasks: {task_count}")
        
        if task_count > 0:
            all_tasks = await db.execute(select(Task))
            for task in all_tasks.scalars().all():
                print(f"  - {task.title} (owner: {task.owner_id}, status: {task.status})")

asyncio.run(check_db())
