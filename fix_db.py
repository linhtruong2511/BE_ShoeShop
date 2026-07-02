import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text


async def fix_gender():
    async with AsyncSessionLocal() as db:
        # Update any 'men' to 'male' and 'women' to 'female'
        await db.execute(
            text("UPDATE Customer SET gender = 'male' WHERE gender = 'men'")
        )
        await db.execute(
            text("UPDATE Customer SET gender = 'female' WHERE gender = 'women'")
        )
        await db.commit()
        print("Database gender values fixed successfully.")


if __name__ == "__main__":
    asyncio.run(fix_gender())
