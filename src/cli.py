import asyncio

import typer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import settings
from src.modules.auth.models import User, UserRole
from src.modules.auth.security import get_password_hash

app = typer.Typer(help="OMS CLI Management Tool")

engine = create_async_engine(settings.DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@app.command()
def version():
    """Показать версию OMS CLI."""
    typer.echo("OMS CLI Version: 0.0.1")


@app.command(name="create-admin")
def create_admin(
    email: str = typer.Argument(..., help="Email администратора"),
    password: str = typer.Argument(..., help="Пароль администратора"),
):
    """Создать пользователя с правами ADMIN."""

    async def _create():
        async with async_session() as session:
            try:
                hashed = get_password_hash(password)
                admin = User(email=email, hashed_password=hashed, role=UserRole.ADMIN, is_active=True)
                session.add(admin)
                await session.commit()
                typer.echo(f"✅ Администратор {email} успешно создан!")
            except IntegrityError:
                typer.echo(f"❌ Ошибка: Пользователь с email {email} уже существует.")
            except Exception as e:
                typer.echo(f"❌ Непредвиденная ошибка: {e}")

    asyncio.run(_create())


if __name__ == "__main__":
    app()
