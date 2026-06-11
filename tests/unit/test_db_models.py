from __future__ import annotations

from sqlalchemy.orm import configure_mappers


def test_sqlalchemy_mappers_configure() -> None:
    configure_mappers()
