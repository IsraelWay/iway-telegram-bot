#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2025.
#  Refactored by: Ainur Iagudin. Copyright (c) 2026.
import logging
from typing import Optional, Dict, Any, List

import pandas as pd
import requests

from bot.sync_telegram_utils import send_telegram_message
from server.model.CalendarEventInfo import CalendarEventInfo
from server.model.ProgramInfo import ProgramInfo
from server.model.AirTableData import AirtableDataFrameWrapper, AirtableConfig, FieldMapper
from settings import Settings


class AirtableRequest:
    def __init__(self, request, required_fields=None, exclude_fields=None):
        if required_fields is None:
            required_fields = []
        if exclude_fields is None:
            exclude_fields = []
        request_data = request.get_json()

        # required
        if "email" in request_data:
            self.email = request_data['email']
        elif "email" not in exclude_fields:
            raise Exception("No required param email")

        if "full_name" in request_data:
            self.full_name = request_data['full_name']
        elif "full_name" not in exclude_fields:
            raise Exception("No required param full_name")

        if "id_record" in request_data:
            self.id_record = request_data['id_record']
        elif "id_record" not in exclude_fields:
            raise Exception("No required param id_record")

        if "tg_id" in request_data:
            self.tg_id = request_data['tg_id']
        elif "tg_id" not in exclude_fields:
            raise Exception("No required param tg_id")

        # not required

        # needed for common ===============================
        if "email_html" in request_data:
            self.email_html = request_data['email_html']
        elif "email_html" in required_fields:
            raise Exception("No required param email_html")

        try:
            self.email_picture = request_data["email_picture"]
        except:
            self.email_picture = "https://thumb.tildacdn.com/tild3033-6631-4636-b931-313031666332/-/format/webp/Screenshot_2023-12-2.png"

        # if "email_picture" in request_data:
        #     self.email_picture = request_data['email_picture']
        # elif "email_picture" in required_fields:
        #     raise Exception("No required param email_picture")

        if "actions" in request_data:
            self.actions = request_data['actions']
        elif "actions" in required_fields:
            raise Exception("No required param actions")

        if "attachments" in request_data:
            self.attachments = request_data['attachments']
        elif "attachments" in required_fields:
            raise Exception("No required param attachments")

        if "main_title" in request_data:
            self.main_title = request_data['main_title']
        elif "main_title" in required_fields:
            raise Exception("No required param main_title")

        if "subject" in request_data:
            self.subject = request_data['subject']
        elif "subject" in required_fields:
            raise Exception("No required param subject")

        if "cc" in request_data:
            self.cc = request_data['cc']
        elif "cc" in required_fields:
            raise Exception("No required param cc")
        else:
            self.cc = request_data.get('cc')
        # ===================================================

        if "invitation_url" in request_data:
            self.invitation_url = request_data['invitation_url']
        elif "invitation_url" in required_fields:
            raise Exception("No required param invitation_url")

        if "support_action" in request_data:
            self.support_action = request_data['support_action']
        elif "support_action" in required_fields:
            raise Exception("No required param support_action")

        if "target" in request_data:
            self.target = request_data['target']
        elif "target" in required_fields:
            raise Exception("No required param target")

        if "consul_info" in request_data:
            self.consul_info = request_data['consul_info']
        elif "consul_info" in required_fields:
            raise Exception("No required param consul_info")

        if "report_ua_url" in request_data:
            self.report_ua_url = request_data['report_ua_url']
        elif "report_ua_url" in required_fields:
            raise Exception("No required param report_ua_url")

        if "agreement_text_url" in request_data:
            self.agreement_text_url = request_data['agreement_text_url']
        elif "agreement_text_url" in required_fields:
            raise Exception("No required param agreement_text_url")

        if "fill_agreement_url" in request_data:
            self.fill_agreement_url = request_data['fill_agreement_url']
        elif "fill_agreement_url" in required_fields:
            raise Exception("No required param fill_agreement_url")

        if "preferred_dates" in request_data:
            self.preferred_dates = request_data['preferred_dates']
        elif "preferred_dates" in required_fields:
            raise Exception("No required param preferred_dates")

        if "anketa_id" in request_data:
            self.anketa_id = request_data['anketa_id']
        elif "anketa_id" in required_fields:
            raise Exception("No required param anketa_id")

        if "avia_dates" in request_data:
            self.avia_dates = request_data['avia_dates']
        elif "avia_dates" in required_fields:
            raise Exception("No required param avia_dates")

        if "reasons" in request_data:
            self.reasons = request_data['reasons']
        elif "reasons" in required_fields:
            raise Exception("No required param reasons")

        if "is_passed" in request_data:
            self.is_passed = request_data['is_passed']
        elif "is_passed" in required_fields:
            raise Exception("No required param is_passed")

        if "anketa_zalog_url" in request_data:
            self.anketa_zalog_url = request_data['anketa_zalog_url']
        elif "anketa_zalog_url" in required_fields:
            raise Exception("No required param anketa_zalog_url")


class ChangeStatusRequest:
    def __init__(self, request):
        data = request.get_json()
        self.id_record = data["id"] if "id" in data else None
        self.new_status = data["new_status"] if "new_status" in data else None
        self.errors = []

    def validate(self):
        if not self.id_record:
            self.errors.append("No required param id")
            return False
        if not self.new_status:
            self.errors.append("No required param new_status")
            return False
        return True

    def apply(self) -> bool:
        base_id = Settings.airtable_base_id()
        table_name = Settings.airtable_leads_table_id()
        api_key = Settings.airtable_api_key()

        url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{self.id_record}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "fields": {
                "Status": self.new_status
            }
        }

        response = requests.patch(url, json=data, headers=headers)

        if response.status_code == 200:
            logging.log(logging.INFO, f"Change status success for record {self.id_record} to {self.new_status}")
            print(f"Change status success for record {self.id_record} to {self.new_status}")
            print(response.json())
            return True

        print(response.status_code, response.text)
        self.errors.append(response.text)
        send_telegram_message(Settings.admin_id(), f"Airtable error: {response.text}")
        return False

class GetAvailableProgramsRequest:
    """Request to get available programs from Airtable."""
    
    def apply(self) -> list[ProgramInfo]:
        """
        Fetch available programs from Airtable.
        
        Returns:
            List of ProgramInfo objects
        """
        table_id = Settings.airtable_programs_template_table_id()
        config = AirtableConfig.from_settings(table_id)
        wrapper = AirtableDataFrameWrapper(config)
        
        try:
            df = wrapper.fetch_records(
                fields=["Официальное название", "Город", "Type"],
                filter_formula="AND({Город} != '', {Город} != BLANK(), {Type} != '', {Type} != BLANK())",
                return_fields_by_id=False
            )
            
            result = []
            for _, row in df.iterrows():
                program = ProgramInfo(
                    id=row.get("id"),
                    name=row.get("Официальное название"),
                    city=row.get("Город"),
                    type=row.get("Type")
                )
                result.append(program)
            
            logging.info(f"Successfully fetched {len(result)} programs")
            return result
            
        except Exception as e:
            logging.error(f"Error fetching programs: {e}")
            return []
    
    def apply_as_dataframe(self) -> pd.DataFrame:
        """
        Fetch available programs as DataFrame.
        
        Returns:
            DataFrame with program information (excluding programs with empty city or type)
        """
        table_id = Settings.airtable_programs_template_table_id()
        config = AirtableConfig.from_settings(table_id)
        wrapper = AirtableDataFrameWrapper(config)
        
        return wrapper.fetch_records(
            fields=["Официальное название", "Город", "Type"],
            filter_formula="AND({Город} != '', {Город} != BLANK(), {Type} != '', {Type} != BLANK())",
            return_fields_by_id=False
        )
    


class RegisterUserRequest:
    """Request to register a new user in Airtable."""
    
    # Field mapping for leads table
    FIELD_MAPPING = {
        "fld8x1yJ12pZjWx1I": "first_name",
        "fldv5IFComRn6ycqk": "last_name",
        "fldszilmfq49ufVKu": "email",
        "fld315yUKT5quZHxh": "comment",
        "fldknTXNnUaZEbcKi": "preferred_programs",
        "fldsMrXJVTiYrKGmd": "phone_number",
        "fldZkOY9uCnZgwfCw": "telegram_id",
        "fldGKDhJLTtvc7ZUb": "status",
        "fldMhwygfz5i67tm6": "utm_source",
        "fld00Twy2CejsX8L9": "utm_medium",
        "fldjsyWSsk9GofHtf": "utm_campaign",
        "fldtHIPrGlW2166eW": "utm_term",
        "fldEZAPzbfYodw8JN": "utm_content",
        "fldMdNTNvtsTllAAr": "target_program",
        "fldFNAV2opllZWgxK": "privacy_policy_agreed",
        "fldjDnFCeNJU4ywgf": "referral"
    }
    
    def __init__(self, request_data: Dict[str, Any]):
        """
        Initialize registration request.
        
        Args:
            request_data: Dictionary with user data
            
        Raises:
            Exception: If required fields are missing
        """
        # Required fields
        required = ["first_name", "last_name", "email", "phone_number", 
                   "telegram_id", "privacy_policy_agreed"]
        
        for field in required:
            if field not in request_data:
                raise Exception(f"No required param {field}")
        
        self.first_name = request_data["first_name"]
        self.last_name = request_data["last_name"]
        self.email = request_data["email"]
        self.phone_number = request_data["phone_number"]
        self.telegram_id = request_data["telegram_id"]
        self.privacy_policy_agreed = request_data["privacy_policy_agreed"]
        
        # Optional fields with defaults
        self.comment = request_data.get("comment", "")
        self.preferred_programs = request_data.get("preferred_programs")
        self.utm_source = request_data.get("utm_source", "-")
        self.utm_medium = request_data.get("utm_medium", "-")
        self.utm_campaign = request_data.get("utm_campaign", "-")
        self.utm_term = request_data.get("utm_term", "-")
        self.utm_content = request_data.get("utm_content", "-")
        self.referral = request_data.get("referral", ["rec0gTSCLKXCn574m"])
        self.target_program = request_data.get("target", "masa")
        self.status = request_data.get("status", "selv3n3t53Wj1E6dk")

    def apply(self) -> bool:
        """
        Register user in Airtable.
        
        Returns:
            True if successful, False otherwise
        """
        table_id = Settings.airtable_leads_table_id()
        config = AirtableConfig.from_settings(table_id)
        wrapper = AirtableDataFrameWrapper(config)
        
        fields = {
            "fld8x1yJ12pZjWx1I": self.first_name,
            "fldv5IFComRn6ycqk": self.last_name,
            "fldszilmfq49ufVKu": self.email,
            "fld315yUKT5quZHxh": self.comment,
            "fldknTXNnUaZEbcKi": self.preferred_programs,
            "fldsMrXJVTiYrKGmd": self.phone_number,
            "fldZkOY9uCnZgwfCw": self.telegram_id,
            "fldGKDhJLTtvc7ZUb": self.status,
            "fldMhwygfz5i67tm6": self.utm_source,
            "fld00Twy2CejsX8L9": self.utm_medium,
            "fldjsyWSsk9GofHtf": self.utm_campaign,
            "fldtHIPrGlW2166eW": self.utm_term,
            "fldEZAPzbfYodw8JN": self.utm_content,
            "fldMdNTNvtsTllAAr": self.target_program,
            "fldFNAV2opllZWgxK": self.privacy_policy_agreed,
            "fldjDnFCeNJU4ywgf": self.referral
        }
        
        logging.info(f"Registering user: {self.first_name} {self.last_name} ({self.email})")
        
        record_id = wrapper.create_record(fields)
        
        if record_id:
            logging.info(f"Successfully registered user with record ID: {record_id}")
            return True
        else:
            logging.error(f"Failed to register user {self.email}")
            return False



class CalendarEventInfoRequest:
    """Request to get calendar event information from Airtable."""
    
    # Predefined table configurations
    TABLE_CONFIGS = {
        "masa": {
            "table_id": "tblNOb28nJXsHdwrf",
            "view": "viwY7oUkaENUDAFVf",
            "field_mapping": {
                "fldoAhFThMUITRPDe": "date",
                "fldj0YbUXN327CsbH": "start_time",
                "fldxKsIvsOub8aQiv": "end_time",
                "fldZ7fbtjgCPm235e": "event_name",
                "fldAyvS7HCA0Rk0sr": "tags",
                "fld31JYAs3bQDKdf1": "subject",
                "fldpX2lGAJLsVIBnC": "address",
                "fldG1J7zXt6lH7dnN": "description",
                "fldcwesZdoxH7CkSk": "map_link",
                "fldl1bRLAbitKHbSh": "files"
            },
            "date_field_id": "fldoAhFThMUITRPDe"
        },
        "onward": {
            "table_id": "tblcsV0OknsNj45As",
            "view": "viwsBQJYW0jaBLy1U",
            "field_mapping": {
                "fldW2Jk6Hb8Xw0i0Z": "date",
                "fldIEI9AUrynJt1kU": "start_time",
                "fldfZiMRnsC3AJ4Gm": "end_time",
                "fldoLZ99gU7aYTCer": "event_name",
                "fld4IYcCYCsx0J3A0": "tags",
                "fldsFtWgpHGbfBMoe": "subject",
                "fldOBMjmxngNxzawP": "address",
                "fldzrT42MddJ5SXpc": "description",
                "fldDRhzgYDLSKigW6": "map_link",
                "fldhGX7fxqWw3qJYo": "files"
            },
            "date_field_id": "fldW2Jk6Hb8Xw0i0Z"
        }
    }
    
    def __init__(self, request_data: Dict[str, Any]):
        """
        Initialize calendar event info request.
        
        Args:
            request_data: Dictionary with request parameters. Can include:
                - type: Name of predefined configuration (e.g., "masa", "onward")
                - table_id: Custom Airtable table ID (overrides config)
                - view: Custom Airtable view ID (overrides config)
                - field_mapping: Custom field mapping (overrides config)
                - date_field_id: Custom date field ID for filtering
                - begin_date, end_date: Date filtering parameters
        """
        print("CalendarEventInfoRequest received data:", request_data)
        
        # Get type from request_data, default to "masa"
        event_type = request_data.get("type", "masa")
        config = self.TABLE_CONFIGS.get(event_type, self.TABLE_CONFIGS["masa"])
        
        # Table configuration (request_data params override config)
        self.table_id = config["table_id"]
        self.field_mapping = config["field_mapping"]
        self.view = config["view"]
        
        # Auto-detect date field from mapping if not provided
        self.date_field_id = config.get("date_field_id")
        
        # Optional date filtering
        self.begin_date = request_data.get("begin_date")
        self.end_date = request_data.get("end_date")
        
        # Optional fields
        self.subject = request_data.get("subject")
        self.description = request_data.get("description", "")
        self.map_link = request_data.get("map_link", "")
        self.address = request_data.get("address")
        self.tags = request_data.get("tags", [])
        self.files = request_data.get("files", [])

    def apply(self) -> pd.DataFrame:
        """
        Fetch calendar events as DataFrame.
        
        Returns:
            DataFrame with calendar events
        """
        config = AirtableConfig.from_settings(self.table_id)
        wrapper = AirtableDataFrameWrapper(config)
        mapper = FieldMapper(self.field_mapping)
        
        fields = list(self.field_mapping.keys())
        
        # Build filter formula based on date range
        filter_formula = None
        if self.date_field_id and (self.begin_date or self.end_date):
            if self.begin_date and self.end_date:
                # Both dates provided - filter between dates
                filter_formula = f"AND(IS_AFTER({{{self.date_field_id}}}, '{self.begin_date}'), IS_BEFORE({{{self.date_field_id}}}, '{self.end_date}'))"
            elif self.begin_date:
                # Only begin date - filter after begin_date
                filter_formula = f"IS_AFTER({{{self.date_field_id}}}, '{self.begin_date}')"
            elif self.end_date:
                # Only end date - filter before end_date
                filter_formula = f"IS_BEFORE({{{self.date_field_id}}}, '{self.end_date}')"
        
        df = wrapper.fetch_records(
            fields=fields,
            view=self.view,
            filter_formula=filter_formula,
            return_fields_by_id=True
        )
        
        # Map field IDs to readable names
        df = mapper.map_to_names(df)
        
        logging.info(f"Fetched {len(df)} calendar events from table {self.table_id}")
        
        return df
    
    def apply_as_list(self) -> list[CalendarEventInfo]:
        """
        Fetch calendar events as list of CalendarEventInfo objects.
        
        Returns:
            List of CalendarEventInfo objects
        """
        df = self.apply()
        
        events = []
        for _, row in df.iterrows():
            # Helper function to convert NaN to None
            def safe_get(key, default=None):
                value = row.get(key, default)
                return None if pd.isna(value) else value
            
            event = CalendarEventInfo(
                id=safe_get("id"),
                date=safe_get("date"),
                start_time=safe_get("start_time"),
                end_time=safe_get("end_time"),
                event_name=safe_get("event_name"),
                tags=safe_get("tags", []),
                subject=safe_get("subject"),
                address=safe_get("address"),
                description=safe_get("description", ""),
                map_link=safe_get("map_link"),
                files=safe_get("files", [])
            )
            events.append(event)
        
        return events



class CalendarDataRequest:
    """Request to get calendar subject data from Airtable."""
    
    # Field mapping for calendar subjects
    FIELD_MAPPING = {
        "fldReJymRoetXn8jE": "name",
        "fldjSoE7IO1vqfIMS": "teacher_id"
    }
    
    def __init__(self, request_data: Optional[Dict[str, Any]] = None):
        """
        Initialize calendar data request.
        
        Args:
            request_data: Optional dictionary with request parameters
        """
        self.request_data = request_data or {}
    
    def apply(self) -> pd.DataFrame:
        """
        Fetch calendar subject data as DataFrame.
        
        Returns:
            DataFrame with subject information
        """
        table_id = "tblKBM5QWCyD97JVf"  # Calendar subjects table
        config = AirtableConfig.from_settings(table_id)
        wrapper = AirtableDataFrameWrapper(config)
        mapper = FieldMapper(self.FIELD_MAPPING)
        
        fields = list(self.FIELD_MAPPING.keys())
        
        df = wrapper.fetch_records(
            fields=fields,
            return_fields_by_id=True
        )
        
        # Map field IDs to readable names
        df = mapper.map_to_names(df)
        
        logging.info(f"Fetched {len(df)} calendar subjects")
        
        return df
    
    def apply_as_list(self) -> List[Dict[str, Any]]:
        """
        Fetch calendar subject data as list of dictionaries.
        
        Returns:
            List of subject dictionaries
        """
        df = self.apply()
        return df.to_dict('records')


class CalendarEventsWithSubjectsRequest:
    """Request to get calendar events joined with subject data."""
    
    @staticmethod
    def _truncate_text(text: str, max_length: int = 32) -> str:
        """
        Truncate text to max_length characters and add ... if truncated.
        
        Args:
            text: Text to truncate
            max_length: Maximum length (default 32)
            
        Returns:
            Truncated text with ... if it exceeds max_length
        """
        if not isinstance(text, str):
            return ""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    @staticmethod
    def _extract_bold_text(text: Any) -> str:
        """
        Extract text from bold markers (**text**).
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            Text from bold markers or empty string if not found
        """
        if not isinstance(text, str) or pd.isna(text):
            return ""
        
        import re
        # Find text between ** markers
        match = re.search(r'\*\*([^*]+)\*\*', text)
        if match:
            return match.group(1).strip()
        
        return ""
    
    @staticmethod
    def _clean_markdown(text: Any) -> str:
        """
        Remove markdown and formatting symbols from text.
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            Clean text without formatting symbols
        """
        if not isinstance(text, str) or pd.isna(text):
            return ""
        
        # Remove markdown bold markers (**)
        text = text.replace("**", "")
        # Remove markdown italic markers (*)
        text = text.replace("*", "")
        # Remove markdown underscore (__)
        text = text.replace("__", "")
        # Remove markdown single underscore (_)
        text = text.replace("_", "")
        # Remove newlines with backslash
        text = text.replace("\\n", " ")
        # Remove actual newlines
        text = text.replace("\n", " ")
        # Remove multiple spaces
        text = " ".join(text.split())
        
        return text.strip()
    
    @staticmethod
    def _truncate_text(text: str, max_length: int = 32) -> str:
        """
        Truncate text to max_length characters and add ... if truncated.
        
        Args:
            text: Text to truncate
            max_length: Maximum length (default 32)
            
        Returns:
            Truncated text with ... if it exceeds max_length
        """
        if not isinstance(text, str):
            return ""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def __init__(self, request_data: Optional[Dict[str, Any]] = None):
        """
        Initialize calendar events with subjects request.
        
        Args:
            request_data: Optional dictionary with request parameters (e.g., date for filtering)
        """
        self.request_data = request_data or {}
    
    def apply(self) -> pd.DataFrame:
        """
        Fetch calendar events and join with subject data and teacher data.
        
        Returns:
            DataFrame with events joined with subject name and teacher name
        """
        # Get calendar events with date range
        # No default dates - let the user specify or get all events
        event_request = CalendarEventInfoRequest(self.request_data)
        events_df = event_request.apply()
        
        if events_df.empty:
            logging.warning("No events found")
            return events_df
        
        # Initialize subject_name and teacher_name columns
        events_df['subject_name'] = None
        events_df['teacher_name'] = None
        
        # If subject column exists, try to join with subjects
        if 'subject' in events_df.columns:
            # Get calendar subjects
            calendar_request = CalendarDataRequest()
            subjects_df = calendar_request.apply()
            
            # Get teachers data
            teachers_config = AirtableConfig.from_settings("tbl1rbYLDLHgmoSld")
            teachers_wrapper = AirtableDataFrameWrapper(teachers_config)
            teachers_df = teachers_wrapper.fetch_records(
                fields=["fldBaOKMIz8JuR0xm"],
                return_fields_by_id=True
            )
            teachers_df.rename(columns={"fldBaOKMIz8JuR0xm": "teacher_name"}, inplace=True)
            
            # Check if subject is present (not empty/NaN) and extract first ID
            def extract_subject_id(x):
                if pd.isna(x):
                    return None
                if isinstance(x, list) and len(x) > 0:
                    return x[0]
                return None
            
            events_df['subject_id'] = events_df['subject'].apply(extract_subject_id)
            
            # Determine which rows have subject data
            has_subject = events_df['subject_id'].notna()
            
            # Join with subjects only for events that have subject
            if has_subject.any():
                subjects_selected = subjects_df[['id', 'name', 'teacher_id']].copy()
                
                # Join only rows with subject_id
                join_rows = events_df[has_subject].merge(
                    subjects_selected,
                    left_on='subject_id',
                    right_on='id',
                    how='left',
                    suffixes=('', '_subject')
                )
                
                # Extract teacher_id from list if it exists
                join_rows['teacher_id_extracted'] = join_rows['teacher_id'].apply(
                    lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
                )
                
                # Join with teachers to get teacher name
                join_rows = join_rows.merge(
                    teachers_df[['id', 'teacher_name']],
                    left_on='teacher_id_extracted',
                    right_on='id',
                    how='left',
                    suffixes=('', '_teacher')
                )
                
                # Copy subject_name and teacher_name back to events_df
                events_df.loc[has_subject, 'subject_name'] = join_rows['name'].values
                events_df.loc[has_subject, 'teacher_name'] = join_rows['teacher_name'].values
        
        # Fill NaN or missing subject_name with cleaned description (from description only)
        if 'description' in events_df.columns:
            no_subject_name = pd.isna(events_df['subject_name'])
            
            # First try to extract bold text (**...** )
            events_df.loc[no_subject_name, 'subject_name'] = events_df.loc[no_subject_name, 'description'].apply(
                lambda x: self._extract_bold_text(x)
            )
            
            # If no bold text found, use cleaned description
            still_empty = pd.isna(events_df['subject_name']) | (events_df['subject_name'] == '')
            events_df.loc[still_empty, 'subject_name'] = events_df.loc[still_empty, 'description'].apply(
                lambda x: self._clean_markdown(x)
            )
            
            # Truncate ONLY subject_name that came from description (still_empty mask tracks these)
            events_df.loc[still_empty, 'subject_name'] = events_df.loc[still_empty, 'subject_name'].apply(self._truncate_text)
        
        # Clean up intermediate columns
        columns_to_drop = ['subject', 'subject_id', 'teacher_id', 'id_subject', 'id_teacher', 'teacher_id_extracted']
        events_df.drop(columns=[col for col in columns_to_drop if col in events_df.columns], inplace=True)
        
        # Replace all NaN with None at DataFrame level - use replace with None
        events_df = events_df.replace({pd.NA: None, pd.NaT: None})
        events_df = events_df.where(pd.notna(events_df), None)
        
        logging.info(f"Processed {len(events_df)} events with subjects and teachers")
        return events_df
    
    def apply_as_list(self) -> List[Dict[str, Any]]:
        """
        Fetch calendar events with subjects as list of dictionaries.
        
        Returns:
            List of event dictionaries with subject information
        """
        df = self.apply()
        return df.to_dict('records')

