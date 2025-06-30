import apps.load_model  # noqa

from .auth.seed import seed_users
from .blogs.seed import seed_blogs
import asyncio


async def seed():
    await seed_users()
    await seed_blogs()
    print("Seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
