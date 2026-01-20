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
    
    # Field mapping for calendar events
    FIELD_MAPPING = {
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
    }
    
    def __init__(self, request_data: Dict[str, Any]):
        """
        Initialize calendar event info request.
        
        Args:
            request_data: Dictionary with request parameters
        """
        print("CalendarEventInfoRequest received data:", request_data)
        
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
        table_id = "tblNOb28nJXsHdwrf"  # Calendar events table
        config = AirtableConfig.from_settings(table_id)
        wrapper = AirtableDataFrameWrapper(config)
        mapper = FieldMapper(self.FIELD_MAPPING)
        
        fields = list(self.FIELD_MAPPING.keys())
        
        # Build filter formula based on date range
        filter_formula = None
        if self.begin_date and self.end_date:
            # Both dates provided - filter between dates
            filter_formula = f"AND(IS_AFTER({{fldoAhFThMUITRPDe}}, '{self.begin_date}'), IS_BEFORE({{fldoAhFThMUITRPDe}}, '{self.end_date}'))"
        elif self.begin_date:
            # Only begin date - filter after begin_date
            filter_formula = f"IS_AFTER({{fldoAhFThMUITRPDe}}, '{self.begin_date}')"
        elif self.end_date:
            # Only end date - filter before end_date
            filter_formula = f"IS_BEFORE({{fldoAhFThMUITRPDe}}, '{self.end_date}')"
        
        df = wrapper.fetch_records(
            fields=fields,
            view="viwY7oUkaENUDAFVf",
            filter_formula=filter_formula,
            return_fields_by_id=True
        )
        
        # Map field IDs to readable names
        df = mapper.map_to_names(df)
        
        logging.info(f"Fetched {len(df)} calendar events")
        
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
            event = CalendarEventInfo(
                id=row.get("id"),
                date=row.get("date"),
                start_time=row.get("start_time"),
                end_time=row.get("end_time"),
                event_name=row.get("event_name"),
                tags=row.get("tags", []),
                subject=row.get("subject"),
                address=row.get("address"),
                description=row.get("description", ""),
                map_link=row.get("map_link"),
                files=row.get("files", [])
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
        
        # The subject field in events contains a list with subject IDs
        # We need to extract the first ID and join
        if not events_df.empty and 'subject' in events_df.columns:
            # Extract first subject ID from list
            events_df['subject_id'] = events_df['subject'].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
            )
            
            # Select only required columns from subjects (id for join, name, teacher_id)
            subjects_selected = subjects_df[['id', 'name', 'teacher_id']].copy()
            
            # Join events with subjects on subject_id = id
            merged_df = events_df.merge(
                subjects_selected,
                left_on='subject_id',
                right_on='id',
                how='left',
                suffixes=('', '_subject')
            )
            
            # Rename subject name column for clarity
            merged_df.rename(columns={'name': 'subject_name'}, inplace=True)
            
            # Extract teacher_id from list if it exists
            merged_df['teacher_id_extracted'] = merged_df['teacher_id'].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
            )
            
            # Join with teachers to get teacher name
            merged_df = merged_df.merge(
                teachers_df[['id', 'teacher_name']],
                left_on='teacher_id_extracted',
                right_on='id',
                how='left',
                suffixes=('', '_teacher')
            )
            
            # Drop unnecessary columns
            columns_to_drop = ['id_subject', 'id_teacher', 'teacher_id', 'teacher_id_extracted']
            merged_df.drop(columns=[col for col in columns_to_drop if col in merged_df.columns], inplace=True)
            
            logging.info(f"Joined {len(merged_df)} events with subjects and teachers")
            return merged_df
        
        logging.warning("No events found or subject column missing")
        return events_df
    
    def apply_as_list(self) -> List[Dict[str, Any]]:
        """
        Fetch calendar events with subjects as list of dictionaries.
        
        Returns:
            List of event dictionaries with subject information
        """
        df = self.apply()
        return df.to_dict('records')

