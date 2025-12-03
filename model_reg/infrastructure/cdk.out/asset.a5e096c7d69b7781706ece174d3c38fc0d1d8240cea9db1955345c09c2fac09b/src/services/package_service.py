# src/services/package_service.py
import os
import sys
import uuid
import zipfile
import base64
from datetime import datetime
from typing import List, Optional, Dict
import boto3
from botocore.exceptions import ClientError

try:
    from ..models import Package, PackageMetadata, PackageVersion
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from models import Package, PackageMetadata, PackageVersion


class PackageService:
    """Service for managing packages in S3 and DynamoDB"""

    def __init__(self):
        self.s3_client = boto3.client("s3")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(os.getenv("DYNAMODB_TABLE_NAME"))
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def create_package(self, metadata: PackageMetadata, zip_data: bytes) -> Package:
        """Upload a new package"""
        package_id = str(uuid.uuid4())
        s3_key = f"packages/{metadata.name}/{metadata.version}/{package_id}.zip"

        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=zip_data,
            ContentType="application/zip",
        )

        # Get size
        size_bytes = len(zip_data)
        metadata.size_bytes = size_bytes

        # Create package record
        now = datetime.utcnow()
        package = Package(
            package_id=package_id,
            metadata=metadata,
            s3_key=s3_key,
            created_at=now,
            updated_at=now,
        )

        # Store in DynamoDB
        self.table.put_item(Item=package.to_dict())

        return package

    def get_package(self, package_id: str) -> Optional[Package]:
        """Retrieve a package by ID"""
        try:
            response = self.table.get_item(Key={"package_id": package_id})
            if "Item" in response:
                return Package.from_dict(response["Item"])
            return None
        except ClientError:
            return None

    def get_package_data(self, package_id: str) -> Optional[bytes]:
        """Download package zip file from S3"""
        package = self.get_package(package_id)
        if not package:
            return None

        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=package.s3_key
            )
            return response["Body"].read()
        except ClientError:
            return None

    def update_package_metadata(
        self, package_id: str, updates: Dict
    ) -> Optional[Package]:
        """Update package metadata"""
        package = self.get_package(package_id)
        if not package:
            return None

        # Update allowed fields
        allowed_fields = [
            "description",
            "author",
            "license",
            "model_card",
            "tags",
            "rating_score",
            "reproducibility_score",
            "reviewedness_score",
            "tree_score",
        ]

        update_expr_parts = []
        expr_attr_values = {}

        for field, value in updates.items():
            if field in allowed_fields:
                update_expr_parts.append(f"{field} = :{field}")
                expr_attr_values[f":{field}"] = value

        if not update_expr_parts:
            return package

        # Add updated_at
        update_expr_parts.append("updated_at = :updated_at")
        expr_attr_values[":updated_at"] = datetime.utcnow().isoformat()

        update_expr = "SET " + ", ".join(update_expr_parts)

        try:
            self.table.update_item(
                Key={"package_id": package_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_values,
            )
            return self.get_package(package_id)
        except ClientError:
            return None

    def delete_package(self, package_id: str) -> bool:
        """Delete a package"""
        package = self.get_package(package_id)
        if not package:
            return False

        try:
            # Delete from S3
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=package.s3_key)

            # Delete from DynamoDB
            self.table.delete_item(Key={"package_id": package_id})
            return True
        except ClientError:
            return False

    def list_packages(
        self,
        name_regex: Optional[str] = None,
        version_query: Optional[str] = None,
        limit: int = 100,
        last_key: Optional[str] = None,
    ) -> Dict:
        """List packages with optional filtering and pagination"""
        scan_kwargs = {"Limit": limit}

        if last_key:
            scan_kwargs["ExclusiveStartKey"] = {"package_id": last_key}

        try:
            response = self.table.scan(**scan_kwargs)
            items = response.get("Items", [])

            # Convert to Package objects
            packages = [Package.from_dict(item) for item in items]

            # Filter by name regex if provided
            if name_regex:
                import re

                pattern = re.compile(name_regex)
                packages = [p for p in packages if pattern.search(p.metadata.name)]

            # Filter by version query if provided
            if version_query:
                filtered = []
                for p in packages:
                    try:
                        version = PackageVersion.from_string(p.metadata.version)
                        if version.matches(version_query):
                            filtered.append(p)
                    except ValueError:
                        # Skip packages with invalid version format
                        continue
                packages = filtered

            # Prepare response
            result = {
                "packages": [p.to_dict() for p in packages],
                "count": len(packages),
            }

            if "LastEvaluatedKey" in response:
                result["next_key"] = response["LastEvaluatedKey"]["package_id"]

            return result
        except ClientError:
            return {"packages": [], "count": 0}

    def search_packages(self, search_text: str, limit: int = 100) -> List[Package]:
        """Search packages by name or model card content"""
        try:
            response = self.table.scan(Limit=limit)
            items = response.get("Items", [])
            packages = [Package.from_dict(item) for item in items]

            # Filter by search text
            search_lower = search_text.lower()
            filtered = []
            for p in packages:
                if search_lower in p.metadata.name.lower() or (
                    p.metadata.model_card
                    and search_lower in p.metadata.model_card.lower()
                ):
                    filtered.append(p)

            return filtered
        except ClientError:
            return []

    def reset_registry(self) -> bool:
        """Reset the registry to empty state"""
        try:
            # Scan all items
            response = self.table.scan()
            items = response.get("Items", [])

            # Delete all packages
            for item in items:
                package_id = item["package_id"]
                self.delete_package(package_id)

            return True
        except ClientError:
            return False

    def get_total_size(self) -> int:
        """Get total size of all packages in bytes"""
        try:
            response = self.table.scan()
            items = response.get("Items", [])
            total = sum(item.get("size_bytes", 0) for item in items)
            return total
        except ClientError:
            return 0
