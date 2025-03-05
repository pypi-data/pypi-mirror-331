# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0
"""The command schemas describe the API for the command model.

These are used internally by the platform and users typically won't encounter them.
"""

from __future__ import annotations

from typing import Any, Literal, Union

import pydantic

from .base import DyffSchemaBaseModel
from .platform import (
    Documented,
    DyffEntityType,
    EntityKindLiteral,
    FamilyMembers,
    Labeled,
    SchemaVersion,
    Status,
)

# ----------------------------------------------------------------------------


# mypy gets confused because 'dict' is the name of a method in DyffBaseModel
_ModelAsDict = dict[str, Any]


class EntityIdentifier(DyffSchemaBaseModel):
    """Identifies a single entity."""

    @staticmethod
    def of(entity: DyffEntityType) -> EntityIdentifier:
        """Create an identifier that identifies the given entity."""
        return EntityIdentifier(kind=entity.kind, id=entity.id)

    kind: EntityKindLiteral = pydantic.Field(description="The .kind of the entity.")
    id: str = pydantic.Field(description="The .id of the entity.")


class FamilyIdentifier(EntityIdentifier):
    """Identifies a single Family entity."""

    kind: Literal["Family"] = "Family"


class Command(SchemaVersion):
    """Base class for Command messages.

    Commands define the API of the "command model" in our CQRS architecture.
    """

    command: Literal[
        "AppendRevisionToHistory",
        "CreateEntity",
        "EditEntityDocumentation",
        "EditEntityLabels",
        "EditFamilyMembers",
        "ForgetEntity",
        "UpdateEntityStatus",
    ]

    # TODO: (DYFF-223) I think that exclude_unset=True should be the default
    # for all schema objects, but I'm unsure of the consequences of making
    # this change and we'll defer it until v1.
    def dict(
        self, *, by_alias: bool = True, exclude_unset=True, **kwargs
    ) -> _ModelAsDict:
        return super().dict(by_alias=by_alias, exclude_unset=exclude_unset, **kwargs)

    def json(self, *, by_alias: bool = True, exclude_unset=True, **kwargs) -> str:
        return super().json(by_alias=by_alias, exclude_unset=exclude_unset, **kwargs)


# ----------------------------------------------------------------------------


class CreateEntity(Command):
    """Create a new entity."""

    command: Literal["CreateEntity"] = "CreateEntity"

    data: DyffEntityType = pydantic.Field(
        description="The full spec of the entity to create."
    )


# ----------------------------------------------------------------------------


class EditEntityDocumentationData(Documented, EntityIdentifier):
    """Payload data for the EditEntityDocumentation command."""


class EditEntityDocumentation(Command):
    """Edit the documentation associated with an entity.

    Setting a documentation field to null/None deletes the corresponding value. To
    preserve the existing value, leave the field *unset*.
    """

    command: Literal["EditEntityDocumentation"] = "EditEntityDocumentation"

    data: EditEntityDocumentationData = pydantic.Field(description="The edit data.")


# ----------------------------------------------------------------------------


class EditEntityLabelsData(Labeled, EntityIdentifier):
    """Payload data for the EditEntityLabels command."""


class EditEntityLabels(Command):
    """Edit the labels associated with an entity.

    Setting a label field to null/None deletes the corresponding value. To preserve the
    existing value, leave the field *unset*.
    """

    command: Literal["EditEntityLabels"] = "EditEntityLabels"

    data: EditEntityLabelsData = pydantic.Field(description="The edit data.")


# ----------------------------------------------------------------------------


class EditFamilyMembersData(FamilyMembers, FamilyIdentifier):
    """Payload data for the EditFamilyMembers command."""


class EditFamilyMembers(Command):
    """Edit the labels associated with an entity.

    Setting a tag value to null/None deletes the corresponding value. To preserve the
    existing value, leave the field *unset*.
    """

    command: Literal["EditFamilyMembers"] = "EditFamilyMembers"

    data: EditFamilyMembersData = pydantic.Field(description="The edit data.")


# ----------------------------------------------------------------------------


class ForgetEntity(Command):
    """Forget (permanently delete) an entity."""

    command: Literal["ForgetEntity"] = "ForgetEntity"

    data: EntityIdentifier = pydantic.Field(description="The entity to forget.")


# ----------------------------------------------------------------------------


class UpdateEntityStatusData(Status, EntityIdentifier):
    """Payload data for the UpdateEntityStatus command."""


class UpdateEntityStatus(Command):
    """Update the status fields of an entity."""

    command: Literal["UpdateEntityStatus"] = "UpdateEntityStatus"

    data: UpdateEntityStatusData = pydantic.Field(description="The status update data.")


# ----------------------------------------------------------------------------


DyffCommandType = Union[
    CreateEntity,
    EditEntityDocumentation,
    EditEntityLabels,
    EditFamilyMembers,
    ForgetEntity,
    UpdateEntityStatus,
]


__all__ = [
    "Command",
    "CreateEntity",
    "DyffCommandType",
    "EditEntityDocumentation",
    "EditEntityDocumentationData",
    "EditEntityLabels",
    "EditEntityLabelsData",
    "EditFamilyMembers",
    "EditFamilyMembersData",
    "EntityIdentifier",
    "FamilyIdentifier",
    "ForgetEntity",
    "UpdateEntityStatus",
    "UpdateEntityStatusData",
]
