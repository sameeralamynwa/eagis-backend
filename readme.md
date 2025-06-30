# opt flow backend

### collaboration instruction

- after cloning and installing packages please run `pre-commit install` to configure the git pre-commit for linting and formating.
- `pre-commit run --all-files` to scan all files

### scripts

- `fastdapi dev --reload` for dev server

### Migrations scripts

- `alembic revision --autogenerate -m "Add new field or table"` add auto
  generated migration after model modification
- `alembic revision -m "Manual change"` add empty migration for manual
  modification
- `alembic upgrade head` to run migration
- `alembic downgrade` to run migration
- `alembic downgrade base` to reset migrtions
- `alembic heads` list of unapplied mirations

### seed db

- `python -m apps.main_seeder`
