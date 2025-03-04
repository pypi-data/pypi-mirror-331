from typing import Optional, List, Dict, Any
from typing_extensions import Literal
from .._models import BaseModel
from datetime import datetime


class ArtifactType(BaseModel):
    value: str


class ArtifactVersionInfo(BaseModel):
    author: str
    date_created: datetime
    description: Optional[str]
    name: str
    id: str
    uri: Optional[str]
    metadata: Optional[Dict[str, Any]]  # Changed to Optional


class Artifact(BaseModel):
    name: str
    author: str
    metadata: Optional[Dict[str, Any]]  # Changed to Optional
    artifact_type: ArtifactType
    date_created: datetime
    description: Optional[str]
    id: str
    is_public: bool
    pending_public_approval: bool
    latest_public_version_artifact: Optional[ArtifactVersionInfo]
    latest_registered_production_version_artifact: Optional[ArtifactVersionInfo]
    latest_registered_staging_version_artifact: Optional[ArtifactVersionInfo]
    latest_version_artifact: Optional[ArtifactVersionInfo]


class ArtifactSpecific(BaseModel):
    name: str
    author: str
    metadata: Optional[Dict[str, Any]]  # Changed to Optional
    date_created: datetime
    description: Optional[str]
    id: str
    is_public: bool
    pending_public_approval: bool
    latest_public_version_artifact: Optional[ArtifactVersionInfo]
    latest_registered_production_version_artifact: Optional[ArtifactVersionInfo]
    latest_registered_staging_version_artifact: Optional[ArtifactVersionInfo]
    latest_version_artifact: Optional[ArtifactVersionInfo]


class ArtifactVersionLatest(BaseModel):
    latest_public_version_artifact: Optional[ArtifactVersionInfo]
    latest_registered_production_version_artifact: Optional[ArtifactVersionInfo]
    latest_registered_staging_version_artifact: Optional[ArtifactVersionInfo]
    latest_version_artifact: Optional[ArtifactVersionInfo]


class ArtifactVersionLatestReturn(BaseModel):
    data: List[ArtifactVersionLatest]


class ArtifactCreated(BaseModel):
    id: str
    name: str
    author: str
    date_created: datetime
    description: Optional[str]
    is_public: bool
    pending_public_approval: bool
    metadata: Optional[Dict[str, Any]]  # Changed to Optional


class ArtifactCreateParams(BaseModel):
    name: str
    description: Optional[str]
    type: str
    metadata: Optional[Dict[str, Any]]  # Changed to Optional
    is_public: bool = False


class ArtifactSpecificCreateParams(BaseModel):
    name: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]  # Changed to Optional
    is_public: bool = False


class ArtifactUpdateReturn(BaseModel):
    id: str
    name: str


class ArtifactUpdated(BaseModel):
    data: List[ArtifactUpdateReturn]
    object: Literal["list"]


class ArtifactUpdateParams(BaseModel):
    data: Dict[str, Any]
    object: Literal["artifact"]

    def __init__(self, **data):
        super().__init__(**data)
        self.data = self.transform_updates()

    def transform_updates(self) -> str:
        return ",".join(f"{k}:{v}" for k, v in self.data.items())


class ArtifactDeleteReturnFields(BaseModel):
    id: str
    name: str


class ArtifactDeleted(BaseModel):
    data: List[ArtifactDeleteReturnFields]  # List can be empty
    object: Literal["list"]


class ArtifactDownloadUrl(BaseModel):
    success: bool
    message: str
    files: List[Dict[str, str]]


class ArtifactQueryResult(BaseModel):
    data: List[Artifact]
    object: Literal["list"]


class ArtifactSpecificQueryResult(BaseModel):
    data: List[ArtifactSpecific]
    object: Literal["list"]
