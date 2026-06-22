from abc import ABC
from pathlib import Path
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from foundation.persistence.repository import Repository


class DocumentRepository(Repository[CodeDocument, Path], ABC): ...
