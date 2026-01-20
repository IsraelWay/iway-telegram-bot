#  Author: Ainur Iagudin. Copyright (c) 2026.
"""
AirTable data models and wrappers for returning data as pandas DataFrames.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import pandas as pd
import requests
import logging
from settings import Settings


@dataclass
class AirtableConfig:
    """Configuration for Airtable API requests."""
    base_id: str
    table_id: str
    api_key: str
    
    @classmethod
    def from_settings(cls, table_id: str) -> 'AirtableConfig':
        """Create config from settings."""
        return cls(
            base_id=Settings.airtable_base_id(),
            table_id=table_id,
            api_key=Settings.airtable_api_key()
        )


class AirtableDataFrameWrapper:
    """
    Base wrapper class for Airtable requests that returns pandas DataFrames.
    Handles pagination, field mapping, and error handling.
    """
    
    def __init__(self, config: AirtableConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard Airtable API headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    def _build_url(self, endpoint: Optional[str] = None) -> str:
        """Build Airtable API URL.

        When endpoint is None, returns the base table URL for creating records.
        Use endpoint="listRecords" for listing records with pagination.
        """
        base = f"https://api.airtable.com/v0/{self.config.base_id}/{self.config.table_id}"
        return f"{base}/{endpoint}" if endpoint else base
    
    def fetch_records(
        self,
        fields: Optional[List[str]] = None,
        filter_formula: Optional[str] = None,
        view: Optional[str] = None,
        return_fields_by_id: bool = True,
        max_records: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch records from Airtable and return as pandas DataFrame.
        
        Args:
            fields: List of field IDs or names to retrieve
            filter_formula: Airtable filter formula
            view: View ID to use
            return_fields_by_id: Whether to return fields by field ID
            max_records: Maximum number of records to fetch
            
        Returns:
            pandas DataFrame with records
        """
        url = self._build_url("listRecords")
        headers = self._get_headers()
        
        params: Dict[str, Any] = {
            "returnFieldsByFieldId": return_fields_by_id
        }
        
        if fields:
            params["fields"] = fields
        if filter_formula:
            params["filterByFormula"] = filter_formula
        if view:
            params["view"] = view
        if max_records:
            params["maxRecords"] = max_records
        
        records = []
        total_fetched = 0
        
        while True:
            try:
                response = requests.post(url, json=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if "records" in data:
                    for record in data["records"]:
                        record_data = {
                            "id": record.get("id"),
                            "created_time": record.get("createdTime"),
                            **record.get("fields", {})
                        }
                        records.append(record_data)
                        total_fetched += 1
                        
                        if max_records and total_fetched >= max_records:
                            break
                
                # Handle pagination
                if "offset" not in data or (max_records and total_fetched >= max_records):
                    break
                    
                params["offset"] = data["offset"]
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching records from Airtable: {e}")
                raise
        
        df = pd.DataFrame(records)
        self.logger.info(f"Fetched {len(records)} records from Airtable table {self.config.table_id}")
        
        return df
    
    def fetch_single_record(self, record_id: str) -> Optional[pd.Series]:
        """
        Fetch a single record by ID.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            pandas Series with record data or None if not found
        """
        url = f"https://api.airtable.com/v0/{self.config.base_id}/{self.config.table_id}/{record_id}"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            record_data = {
                "id": data.get("id"),
                "created_time": data.get("createdTime"),
                **data.get("fields", {})
            }
            
            return pd.Series(record_data)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching record {record_id}: {e}")
            return None
    
    def update_record(self, record_id: str, fields: Dict[str, Any]) -> bool:
        """
        Update a record in Airtable.
        
        Args:
            record_id: Airtable record ID
            fields: Dictionary of field IDs/names and values to update
            
        Returns:
            True if successful, False otherwise
        """
        url = f"https://api.airtable.com/v0/{self.config.base_id}/{self.config.table_id}/{record_id}"
        headers = self._get_headers()
        
        data = {"fields": fields}
        
        try:
            response = requests.patch(url, json=data, headers=headers)
            response.raise_for_status()
            self.logger.info(f"Successfully updated record {record_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating record {record_id}: {e}")
            return False
    
    def create_record(self, fields: Dict[str, Any]) -> Optional[str]:
        """
        Create a new record in Airtable.
        
        Args:
            fields: Dictionary of field IDs/names and values
            
        Returns:
            Created record ID or None if failed
        """
        # Creating records should POST to the table URL (no listRecords endpoint)
        url = self._build_url()
        headers = self._get_headers()
        
        data = {"fields": fields}
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            record_id = response.json().get("id")
            self.logger.info(f"Successfully created record {record_id}")
            return record_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating record: {e}")
            return None
    
    def delete_record(self, record_id: str) -> bool:
        """
        Delete a record from Airtable.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            True if successful, False otherwise
        """
        url = f"https://api.airtable.com/v0/{self.config.base_id}/{self.config.table_id}/{record_id}"
        headers = self._get_headers()
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            self.logger.info(f"Successfully deleted record {record_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error deleting record {record_id}: {e}")
            return False


class FieldMapper:
    """Helper class to map between field IDs and human-readable names."""
    
    def __init__(self, field_mapping: Dict[str, str]):
        """
        Initialize field mapper.
        
        Args:
            field_mapping: Dict mapping field_id to field_name
        """
        self.field_mapping = field_mapping
        self.reverse_mapping = {v: k for k, v in field_mapping.items()}
    
    def map_to_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map DataFrame columns from field IDs to names.
        
        Args:
            df: DataFrame with field ID columns
            
        Returns:
            DataFrame with named columns
        """
        return df.rename(columns=self.field_mapping)
    
    def map_to_ids(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map dictionary keys from field names to IDs.
        
        Args:
            data: Dictionary with field name keys
            
        Returns:
            Dictionary with field ID keys
        """
        return {self.reverse_mapping.get(k, k): v for k, v in data.items()}
