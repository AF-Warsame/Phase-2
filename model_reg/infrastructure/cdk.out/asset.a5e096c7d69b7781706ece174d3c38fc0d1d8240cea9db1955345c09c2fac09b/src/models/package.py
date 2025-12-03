# src/models/package.py
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class PackageVersion:
    """Represents a semantic version"""

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> "PackageVersion":
        """Parse version string like '1.2.3'"""
        parts = version_str.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def matches(self, query: str) -> bool:
        """Check if version matches a query pattern"""
        if query.startswith("^"):
            # Caret: compatible with version
            target = PackageVersion.from_string(query[1:])
            return self.major == target.major and (
                self.minor > target.minor
                or (self.minor == target.minor and self.patch >= target.patch)
            )
        elif query.startswith("~"):
            # Tilde: approximately equivalent
            target = PackageVersion.from_string(query[1:])
            return (
                self.major == target.major
                and self.minor == target.minor
                and self.patch >= target.patch
            )
        elif "-" in query:
            # Range: e.g., "1.0.0-2.0.0"
            start, end = query.split("-")
            start_v = PackageVersion.from_string(start)
            end_v = PackageVersion.from_string(end)
            return start_v <= self <= end_v
        else:
            # Exact match
            return str(self) == query

    def __eq__(self, other):
        if not isinstance(other, PackageVersion):
            return False
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other):
        if not isinstance(other, PackageVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other):
        return self == other or self < other


@dataclass
class PackageMetadata:
    """Metadata for a package"""

    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = None
    repository_url: Optional[str] = None
    huggingface_url: Optional[str] = None
    model_card: Optional[str] = None
    tags: List[str] = None
    dependencies: List[str] = None
    rating_score: Optional[float] = None
    reproducibility_score: Optional[float] = None
    reviewedness_score: Optional[float] = None
    tree_score: Optional[float] = None
    size_bytes: Optional[int] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Package:
    """Represents a complete package"""

    package_id: str
    metadata: PackageMetadata
    s3_key: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for DynamoDB"""
        return {
            "package_id": self.package_id,
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "license": self.metadata.license,
            "repository_url": self.metadata.repository_url,
            "huggingface_url": self.metadata.huggingface_url,
            "model_card": self.metadata.model_card,
            "tags": self.metadata.tags,
            "dependencies": self.metadata.dependencies,
            "rating_score": self.metadata.rating_score,
            "reproducibility_score": self.metadata.reproducibility_score,
            "reviewedness_score": self.metadata.reviewedness_score,
            "tree_score": self.metadata.tree_score,
            "size_bytes": self.metadata.size_bytes,
            "s3_key": self.s3_key,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Package":
        """Create from DynamoDB dictionary"""
        metadata = PackageMetadata(
            name=data["name"],
            version=data["version"],
            description=data.get("description"),
            author=data.get("author"),
            license=data.get("license"),
            repository_url=data.get("repository_url"),
            huggingface_url=data.get("huggingface_url"),
            model_card=data.get("model_card"),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            rating_score=data.get("rating_score"),
            reproducibility_score=data.get("reproducibility_score"),
            reviewedness_score=data.get("reviewedness_score"),
            tree_score=data.get("tree_score"),
            size_bytes=data.get("size_bytes"),
        )
        return cls(
            package_id=data["package_id"],
            metadata=metadata,
            s3_key=data["s3_key"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
