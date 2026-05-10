from django.db.models import Model

from db.models import Table
from entities.table_entity import TableEntity
from repositories.base import BaseRepository


class TableRepository(BaseRepository[TableEntity, Table]):
    """
    Repository for managing Table data access.

    This class handles all database operations related to the restaurant's
    tables, shielding the business logic (Services) from Django ORM specifics
    and returning pure Python entities.
    """
    def __init__(self, entity: type[TableEntity] = TableEntity, model: type[Model] = Table):
        """
        Initializes the table repository.

        Args:
            entity (type[TableEntity]): The dataclass used to represent a table.
            model (type[Model]): The Django ORM model for the database table.
        """
        super().__init__(entity, model)

    def _to_entity(self, model: Table) -> TableEntity:
        """
        Maps a Django ORM Table model instance to a TableEntity dataclass.

        Args:
            model (Table): The database model instance.

        Returns:
            TableEntity: A clean data transfer object representing the table.
        """
        return self.entity(
            id=model.id,
            name=model.name
        )

    def get_all(self) -> list[TableEntity]:
        """
        Retrieves all available tables from the database.

        Returns:
            list[TableEntity]: A list of all tables represented as entities.
        """
        return [self._to_entity(table) for table in self.model.objects.all()]

    def exclude_by_ids(self, exclude_ids: list[int]) -> list[TableEntity]:
        """
        Retrieves all tables except those whose IDs are in the provided list.

        This method is optimized using the `.only()` ORM method to fetch
        only the necessary columns ('id', 'name') from the database,
        reducing memory footprint and query execution time.

        Args:
            exclude_ids (list[int]): A list of table IDs to exclude from the result.

        Returns:
            list[TableEntity]: A list of the remaining available tables.
        """
        return [
            self._to_entity(table) for table in self.model.objects.exclude(id__in=exclude_ids).only('id', 'name')
        ]

    def exists(self, table_id: int) -> bool:
        """
        Checks if a table with the specified ID exists in the database.

        Args:
            table_id (int): The ID of the table to look up.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        return self.model.objects.filter(id=table_id).exists()
