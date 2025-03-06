from dataclasses import asdict, dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Report:
    columns: List[str]
    description: str
    descriptionTranslations: Dict[str, str]
    displayName: str
    displayNameTranslations: Dict[str, str]
    internalName: str
    querySyntax: str
    reportCategories: List[str]
    id: str
    projectId: str
    tenant: str

    def to_dict(self):
        return asdict(self)