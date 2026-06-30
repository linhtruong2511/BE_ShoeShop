import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_users():
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        # To keep it simple, we just insert.
        admin = User(
            username="admin",
            password_hash=pwd_context.hash("Admin@123"),
            full_name="Administrator",
            email="admin@shoeshop.com",
            role="admin",
            status="active"
        )
        staff = User(
            username="staff1",
            password_hash=pwd_context.hash("Staff@123"),
            full_name="Staff Member",
            email="staff1@shoeshop.com",
            role="staff",
            status="active"
        )
        
        session.add(admin)
        session.add(staff)
        try:
            await session.commit()
            print("Seed data created successfully.")
        except Exception as e:
            print(f"Error seeding data (maybe already exists): {e}")

if __name__ == "__main__":
    asyncio.run(seed_users())
