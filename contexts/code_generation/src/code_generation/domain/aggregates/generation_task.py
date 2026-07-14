from foundation.building_blocks.aggregate_root import AggregateRoot

from code_generation.domain.identities.generation_task_id import GenerationTaskId


class GenerationTask(AggregateRoot[GenerationTaskId]):
    ...
    