from sqlalchemy import select
from core.db import get_session
from .models import Blog, BlogCategory
from sqlalchemy.ext.asyncio import AsyncSession

dummy_blog = """In the past two decades, small studies
demonstrated that London taxi drivers tend to have an enlargement
in one area of the hippocampus, a part of the brain involved with
developing spatial memory. Interestingly, that part of the brain is
one area that's commonly damaged by AD.These observations led to
speculation that taxi drivers might be less prone to AD than people
with jobs that don't require similar navigation and spatial processing skills.
A recent study explores this possibility by analyzing data from nearly nine
million people who died over a three-year period and had occupation information
on their death certificates. After accounting for age of death, researchers
tallied Alzheimer's-related death rates for more than 443 different jobs.
The results were dramatic."""


async def seed_blogs():
    session_gen = get_session()
    session: AsyncSession = await anext(session_gen)
    category_health_tip = await session.scalar(
        select(BlogCategory).where(BlogCategory.slug == "health-tips")
    )
    category_ai = await session.scalar(
        select(BlogCategory).where(BlogCategory.slug == "ai")
    )
    category_nutrition = await session.scalar(
        select(BlogCategory).where(BlogCategory.slug == "nutrition")
    )

    blog_one = await session.scalar(
        select(Blog).where(Blog.slug == "emsalmonellaem-is-sneaky-watch-out")
    )

    blog_two = await session.scalar(
        select(Blog).where(
            Blog.slug == "two-jobs-may-lower-the-odds-of-dying-from-alzheimers-disease"
        )
    )

    if not category_health_tip:
        category_health_tip = BlogCategory(
            slug="health-tips",
            name="Health Tips",
            short_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            meta_title="Health Categories dimension",
            meta_keywords="Physical abnormalities and syndromes",
            meta_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
        )

    if not category_ai:
        category_ai = BlogCategory(
            slug="ai",
            name="Ai",
            short_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            meta_title="Health Categories dimension",
            meta_keywords="Physical abnormalities and syndromes",
            meta_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
        )

    if not category_nutrition:
        category_nutrition = BlogCategory(
            slug="nutrition",
            name="Nutrition",
            short_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            meta_title="Health Categories dimension",
            meta_keywords="Physical abnormalities and syndromes",
            meta_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
        )

    if not blog_one:
        blog_one = Blog(
            slug="emsalmonellaem-is-sneaky-watch-out",
            title="Salmonella is sneaky: Watch out",
            short_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            content=dummy_blog,
            meta_title="Health Categories dimension",
            meta_keywords="Physical abnormalities and syndromes",
            meta_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            category=category_nutrition,
        )

    if not blog_two:
        blog_two = Blog(
            slug="two-jobs-may-lower-the-odds-of-dying-from-alzheimers-disease",
            title="Two jobs may lower the odds of dying from Alzheimer's disease — but why?",
            short_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            content=dummy_blog,
            meta_title="Health Categories dimension",
            meta_keywords="Physical abnormalities and syndromes",
            meta_desc="""There are 21 separate categories
            which encompass all diseases, conditions and areas
            of health. Each of the Health Categories includes research
            into both disease and normal function""",
            category=category_nutrition,
        )

    session.add(category_nutrition)
    session.add(category_ai)
    session.add(category_health_tip)
    session.add(blog_one)
    session.add(blog_two)
    await session.commit()
    print("Blogs Seeded")
