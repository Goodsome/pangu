from __future__ import annotations
from codegen.code_metadata.application.dtos.module_dto import ModuleDto
from codegen.code_metadata.domain.aggregates.module import DirectoryModule
from codegen.code_metadata.domain.aggregates.module import ExternalModule
from codegen.code_metadata.domain.aggregates.module import FileModule
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.code_metadata.domain.enums.module_kind import ModuleKind
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.value_objects.module_dependency import (
    ModuleDependency,
)
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.code_metadata.infrastructure.mappers.component_v2_mapper import (
    ComponentV2Mapper,
)
from codegen.code_metadata.infrastructure.orm_models.module_model import (
    DirectoryModuleModel,
)
from codegen.code_metadata.infrastructure.orm_models.module_model import (
    ExternalModuleModel,
)
from codegen.code_metadata.infrastructure.orm_models.module_model import FileModuleModel
from codegen.code_metadata.infrastructure.orm_models.module_model import ModuleModel


class ModuleMapper:

    @classmethod
    def to_dto(cls, orm_model: ModuleModel) -> ModuleDto:
        return ModuleDto(
            id=str(orm_model.id),
            name=orm_model.name,
            path=orm_model.path,
            kind=ModuleKind(orm_model.kind),
            dir_module_id=(
                str(orm_model.dir_module_id) if orm_model.dir_module_id else None
            ),
        )

    @classmethod
    def to_domain(
        cls, orm_model: ModuleModel
    ) -> FileModule | DirectoryModule | ExternalModule:
        match orm_model.kind:
            case ModuleKind.FILE:
                return cls._to_file_module(orm_model)
            case ModuleKind.DIRECTORY:
                return cls._to_directory_module(orm_model)
            case ModuleKind.EXTERNAL:
                return cls._to_external_module(orm_model)
            case _:
                raise ValueError(f"Unknown module kind: {orm_model.kind}")

    @classmethod
    def _to_file_module(cls, orm_model: ModuleModel) -> FileModule:
        assert isinstance(orm_model, FileModuleModel)
        return FileModule(
            id=ModuleId.reconstitute(orm_model.id),
            name=orm_model.name,
            path=orm_model.path,
            components=[ComponentV2Mapper.to_domain(c) for c in orm_model.components],
            dependencies=[
                ModuleDependency.model_validate(d) for d in orm_model.dependencies
            ],
            dir_module_id=(
                ModuleId.reconstitute(orm_model.dir_module_id)
                if orm_model.dir_module_id
                else None
            ),
        )

    @classmethod
    def _to_directory_module(cls, orm_model: ModuleModel) -> DirectoryModule:
        assert isinstance(orm_model, DirectoryModuleModel)
        return DirectoryModule(
            id=ModuleId.reconstitute(orm_model.id),
            name=orm_model.name,
            path=orm_model.path,
            public_component_ids=[
                ReferenceTarget.model_validate(r)
                for r in orm_model.public_component_ids
            ],
            sub_module_ids=[ModuleId.reconstitute(s) for s in orm_model.sub_module_ids],
            dir_module_id=(
                ModuleId.reconstitute(orm_model.dir_module_id)
                if orm_model.dir_module_id
                else None
            ),
        )

    @classmethod
    def _to_external_module(cls, orm_model: ModuleModel) -> ExternalModule:
        assert isinstance(orm_model, ExternalModuleModel)
        return ExternalModule(
            id=ModuleId.reconstitute(orm_model.id),
            name=orm_model.name,
            path=orm_model.path,
            components=[ComponentV2Mapper.to_domain(c) for c in orm_model.components],
        )

    @classmethod
    def to_orm(cls, domain_entity: Module) -> ModuleModel:
        match domain_entity.kind:
            case ModuleKind.FILE:
                return cls._file_to_orm(domain_entity)
            case ModuleKind.DIRECTORY:
                return cls._directory_to_orm(domain_entity)
            case ModuleKind.EXTERNAL:
                return cls._external_to_orm(domain_entity)
            case _:
                raise ValueError(f"Unknown module kind: {domain_entity.kind}")

    @classmethod
    def _file_to_orm(cls, domain_entity: FileModule) -> FileModuleModel:
        return FileModuleModel(
            id=domain_entity.id.value,
            kind=domain_entity.kind.value,
            name=domain_entity.name,
            path=domain_entity.path,
            dependencies=[
                d.model_dump(mode="json") for d in domain_entity.dependencies
            ],
            dir_module_id=(
                domain_entity.dir_module_id.value
                if domain_entity.dir_module_id
                else None
            ),
            components=[ComponentV2Mapper.to_orm(c) for c in domain_entity.components],
        )

    @classmethod
    def _directory_to_orm(cls, domain_entity: DirectoryModule) -> DirectoryModuleModel:
        return DirectoryModuleModel(
            id=domain_entity.id.value,
            kind=domain_entity.kind.value,
            name=domain_entity.name,
            path=domain_entity.path,
            public_component_ids=[
                r.model_dump(mode="json") for r in domain_entity.public_component_ids
            ],
            sub_module_ids=[str(s) for s in domain_entity.sub_module_ids],
            dir_module_id=(
                domain_entity.dir_module_id.value
                if domain_entity.dir_module_id
                else None
            ),
        )

    @classmethod
    def _external_to_orm(cls, domain_entity: ExternalModule) -> ExternalModuleModel:
        return ExternalModuleModel(
            id=domain_entity.id.value,
            kind=domain_entity.kind.value,
            name=domain_entity.name,
            path=domain_entity.path,
            components=[ComponentV2Mapper.to_orm(c) for c in domain_entity.components],
        )
