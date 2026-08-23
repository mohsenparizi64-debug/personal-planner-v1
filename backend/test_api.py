import asyncio
import httpx
from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from app.models.all_models import User
from sqlalchemy import select

async def test_api():
    # Get the user
    async with AsyncSessionLocal() as db:
        users_result = await db.execute(select(User))
        user = users_result.scalars().first()
        if not user:
            print("No user found")
            return
        
        print(f"User: {user.email} (ID: {user.id})")
        
        # Create a token for this user
        token = create_access_token({"sub": str(user.id)})
        print(f"Generated token: {token[:50]}...")
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/v1/dashboard/overview",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"\nAPI Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Tasks returned: {len(data.get('tasks', []))}")
                print(f"First few tasks:")
                for task in data.get('tasks', [])[:5]:
                    print(f"  - {task['title']} (status: {task['status']})")
            else:
                print(f"Error: {response.text}")

asyncio.run(test_api())
