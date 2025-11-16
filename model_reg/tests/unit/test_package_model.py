# tests/unit/test_package_model.py
import pytest
from datetime import datetime
from src.models.package import Package, PackageMetadata, PackageVersion


class TestPackageVersion:
    def test_from_string_valid(self):
        version = PackageVersion.from_string("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
    
    def test_from_string_invalid(self):
        with pytest.raises(ValueError):
            PackageVersion.from_string("1.2")
    
    def test_string_conversion(self):
        version = PackageVersion(1, 2, 3)
        assert str(version) == "1.2.3"
    
    def test_exact_match(self):
        version = PackageVersion(1, 2, 3)
        assert version.matches("1.2.3")
        assert not version.matches("1.2.4")
    
    def test_caret_match(self):
        version = PackageVersion(1, 3, 0)
        assert version.matches("^1.2.3")
        assert not version.matches("^2.0.0")
        
        version2 = PackageVersion(1, 2, 4)
        assert version2.matches("^1.2.3")
    
    def test_tilde_match(self):
        version = PackageVersion(1, 2, 5)
        assert version.matches("~1.2.3")
        assert not version.matches("~1.3.0")
    
    def test_range_match(self):
        version = PackageVersion(1, 5, 0)
        assert version.matches("1.0.0-2.0.0")
        assert not version.matches("2.0.0-3.0.0")
    
    def test_equality(self):
        v1 = PackageVersion(1, 2, 3)
        v2 = PackageVersion(1, 2, 3)
        v3 = PackageVersion(1, 2, 4)
        
        assert v1 == v2
        assert v1 != v3
    
    def test_comparison(self):
        v1 = PackageVersion(1, 2, 3)
        v2 = PackageVersion(1, 2, 4)
        v3 = PackageVersion(2, 0, 0)
        
        assert v1 < v2
        assert v1 < v3
        assert v2 < v3
        assert v1 <= v2
        assert v1 <= v1


class TestPackageMetadata:
    def test_creation_minimal(self):
        metadata = PackageMetadata(name="test-package", version="1.0.0")
        assert metadata.name == "test-package"
        assert metadata.version == "1.0.0"
        assert metadata.tags == []
        assert metadata.dependencies == []
    
    def test_creation_full(self):
        metadata = PackageMetadata(
            name="test-package",
            version="1.0.0",
            description="Test package",
            author="Test Author",
            license="MIT",
            tags=["ml", "nlp"],
            dependencies=["numpy", "torch"]
        )
        assert metadata.description == "Test package"
        assert len(metadata.tags) == 2
        assert len(metadata.dependencies) == 2


class TestPackage:
    def test_to_dict(self):
        metadata = PackageMetadata(name="test", version="1.0.0")
        package = Package(
            package_id="123",
            metadata=metadata,
            s3_key="packages/test/1.0.0/123.zip",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        data = package.to_dict()
        assert data["package_id"] == "123"
        assert data["name"] == "test"
        assert data["version"] == "1.0.0"
        assert "created_at" in data
    
    def test_from_dict(self):
        data = {
            "package_id": "123",
            "name": "test",
            "version": "1.0.0",
            "description": "Test package",
            "author": None,
            "license": "MIT",
            "repository_url": None,
            "huggingface_url": None,
            "model_card": None,
            "tags": ["ml"],
            "dependencies": [],
            "rating_score": 0.8,
            "reproducibility_score": 0.7,
            "reviewedness_score": 0.6,
            "tree_score": 0.9,
            "size_bytes": 1024,
            "s3_key": "packages/test/1.0.0/123.zip",
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00"
        }
        
        package = Package.from_dict(data)
        assert package.package_id == "123"
        assert package.metadata.name == "test"
        assert package.metadata.rating_score == 0.8
        assert len(package.metadata.tags) == 1
