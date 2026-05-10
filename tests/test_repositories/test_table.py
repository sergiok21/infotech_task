from entities.table_entity import TableEntity
from tests.test_repositories.base import *


@pytest.mark.django_db
def test_get_all_tables(table_repo, table_1, table_2):
    tables = table_repo.get_all()

    assert len(tables) == 2

    expected_table_1 = TableEntity(id=table_1.id, name=table_1.name)
    expected_table_2 = TableEntity(id=table_2.id, name=table_2.name)

    assert expected_table_1 in tables
    assert expected_table_2 in tables


@pytest.mark.django_db
def test_get_excluding_by_ids(table_repo, table_1, table_2):
    expected_table_2 = TableEntity(id=table_2.id, name=table_2.name)

    tables = table_repo.exclude_by_ids([table_1.id])
    assert len(tables) == 1
    assert tables[0] == expected_table_2

    tables_no_exclude = table_repo.exclude_by_ids([999])
    assert len(tables_no_exclude) == 2

    tables_empty = table_repo.exclude_by_ids([table_1.id, table_2.id])
    assert len(tables_empty) == 0


@pytest.mark.django_db
def test_table_exists(table_repo, table_1):
    assert table_repo.exists(table_1.id) is True

    assert table_repo.exists(999) is False
