from __future__ import absolute_import

import re  # noqa: F401
from abc import ABC, abstractmethod
from typing import List

# python 2 and python 3 compatibility library
import six

from conductor.client.http.api_client import ApiClient
from conductor.client.http.models.prompt_template import PromptTemplate
from conductor.client.http.models.schema_def import SchemaDef
from conductor.client.orkes.models.metadata_tag import MetadataTag


class SchemaClient(ABC):

    @abstractmethod
    def register_schema(self, schema: SchemaDef) -> None:
        """
        Register a new schema.
        """
        pass

    @abstractmethod
    def get_schema(self, schema_name: str, version: int) -> SchemaDef:
        """
        Retrieve a schema by its name and version.
        """
        pass

    @abstractmethod
    def get_all_schemas(self) -> List[SchemaDef]:
        """
        Retrieve all schemas.
        """
        pass

    @abstractmethod
    def delete_schema(self, schema_name: str, version: int) -> None:
        """
        Delete a schema by its name and version.
        """
        pass

    @abstractmethod
    def delete_schema_by_name(self, schema_name: str) -> None:
        """
        Delete all the versions of a schema by its name
        """
        pass