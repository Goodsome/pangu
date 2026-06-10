from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.application.dtos.path_scan_criteria import PathScanCriteria
from codegen.code_metadata.application.dtos.scan_result import ScanResult


class SourceCodeScanner(ABC):

    @abstractmethod
    def discover_files(self, criteria: PathScanCriteria) -> list[ScanResult]: ...
