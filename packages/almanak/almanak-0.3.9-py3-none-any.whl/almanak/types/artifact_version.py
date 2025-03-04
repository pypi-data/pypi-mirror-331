from typing import Optional, List, Dict, Any, Literal
from .._models import BaseModel
from datetime import datetime


class ArtifactVersion(BaseModel):
    name: str
    id: str
    description: Optional[str]
    date_created: datetime
    metadata: Optional[Dict[str, Any]]  # Changed to Optional
    author: str
    is_public: bool
    artifact: Dict[str, str]


class ArtifactVersionRetrieved(BaseModel):
    data: List[ArtifactVersion]
    object: Literal["list"]


class ArtifactVersionList(BaseModel):
    versions: List[ArtifactVersion]


class ArtifactVersionWithType(BaseModel):
    name: str
    author: str
    date_created: datetime
    description: Optional[str]
    is_public: bool
    metadata: Optional[Dict[str, Any]]  # Changed to Optional
    artifact: Dict[str, str]


class ArtifactVersionQueryResult(BaseModel):
    versions: List[ArtifactVersionWithType]


class ArtifactVersionInfo(BaseModel):
    author: str
    date_created: datetime
    description: Optional[str]
    name: str
    id: str
    uri: Optional[str]
    metadata: Optional[Dict[str, Any]]  # Changed to Optional


class ArtifactVersionArtifactReturn(BaseModel):
    name: str


class ArtifactVersionUpdateReturn(BaseModel):
    id: str
    artifact: ArtifactVersionArtifactReturn
    name: str


class ArtifactVersionUpdated(BaseModel):
    data: List[ArtifactVersionUpdateReturn]
    object: Literal["list"]


class ArtifactUpdatedReturn(BaseModel):
    returning: List[ArtifactVersionUpdateReturn]


class ArtifactVersionUpdateParams(BaseModel):
    updates: Dict[str, Any]

    def __init__(self, **data):
        super().__init__(**data)
        self.updates = self.transform_updates()

    def transform_updates(self) -> str:
        return ",".join(f"{k}:{v}" for k, v in self.updates.items())


class PresignedUrl(BaseModel):
    id: str
    presigned_url: str
    relative_path: str


class ArtifactVersionUploaded(BaseModel):
    success: bool
    message: str
    version: str
    versionId: str
    rootUri: str
    urls: List[PresignedUrl]


class ArtifactDownloadUrl(BaseModel):
    success: bool
    message: str
    files: List[PresignedUrl]


class ArtifactUploadUrl(BaseModel):
    success: bool
    urls: List[PresignedUrl]


class ArtifactFile(BaseModel):
    id: str
    uri: str
    date_created: datetime
    description: Optional[str]


class ArtifactFileReturn(BaseModel):
    data: List[ArtifactFile]
    object: Literal["list"]
