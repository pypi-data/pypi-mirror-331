from dataclasses import dataclass

MAX_UC_ENTITY_NAME_LEN = 63  # max length of UC entity name


@dataclass(frozen=True)
class UnityCatalogEntity:
    """Helper data class representing a Unity Catalog entity.

    Attributes:
        catalog (str): The catalog name.
        schema (str): The schema name.
        entity (str): The entity name.
    """

    catalog: str
    schema: str
    entity: str

    @staticmethod
    def from_fullname(fullname: str):
        parts = fullname.split(".")
        assert len(parts) == 3

        return UnityCatalogEntity(catalog=parts[0], schema=parts[1], entity=parts[2])

    @property
    def fullname(self):
        return f"{self.catalog}.{self.schema}.{self.entity}"
