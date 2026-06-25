from foundation.building_blocks.value_object import ValueObject


class Location(ValueObject):
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    