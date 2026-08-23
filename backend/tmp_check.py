import asyncio
from app.crud.roadmap import get_sub_goals
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        result = await get_sub_goals(db, 1, 1)
        print('count', len(result))
        if result:
            print(result[0].tasks)

asyncio.run(main())
