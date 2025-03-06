import os
import random
import string
from datetime import datetime

import pytz

from groclake.datalake import Datalake
from dotenv import load_dotenv

joblake_mapping = {
    "properties": {
        "job_title": {"type": "text"},
        "job_department": {"type": "text"},
        "job_location": {
            "properties": {
                "city": {"type": "text"},
                "state": {"type": "text"},
                "country": {"type": "text"},
                "remote": {"type": "boolean"}
            }
        },
        "company_name": {"type": "text"},
        "company_industry": {"type": "text"},
        "company_size": {"type": "keyword"},
        "employment_type": {"type": "keyword"},
        "experience_required": {"type": "text"},
        "education_required": {
            "type": "nested",
            "properties": {
                "degree": {"type": "keyword"},
                "major": {"type": "text"},
                "preferred_university": {"type": "text"}
            }
        },
        "skills_required": {"type": "keyword"},
        "preferred_certifications": {
            "type": "nested",
            "properties": {
                "name": {"type": "text"},
                "issuing_organization": {"type": "text"}
            }
        },
        "job_responsibilities": {"type": "text"},
        "preferred_experience": {
            "type": "nested",
            "properties": {
                "designation": {"type": "text"},
                "industry": {"type": "text"},
                "company_type": {"type": "text"},
                "min_years": {"type": "integer"},
                "max_years": {"type": "integer"}
            }
        },
        "languages_required": {
            "type": "nested",
            "properties": {
                "language": {"type": "text"},
                "proficiency": {"type": "keyword"}
            }
        },
        "technologies_used": {"type": "keyword"},
        "compensation": {
            "properties": {
                "salary_range": {
                    "properties": {
                        "min": {"type": "keyword"},
                        "max": {"type": "keyword"}
                    }
                },
                "equity": {"type": "boolean"},
                "bonuses": {"type": "boolean"}
            }
        },
        "benefits": {"type": "keyword"},
        "company_culture": {"type": "text"},
        "recruiter_contact": {
            "properties": {
                "name": {"type": "text"},
                "email": {"type": "keyword"},
                "phone": {"type": "keyword"}
            }
        },
        "application_deadline": {"type": "date", "format": "yyyy-MM-dd"}
    }
}

load_dotenv()


class Config:
    ES_CONFIG = {
        "host": os.getenv("ES_HOST"),
        "port": int(os.getenv("ES_PORT")),
        "api_key": os.getenv("ES_API_KEY"),
        "schema": os.getenv("ES_SCHEMA")
    }

    MYSQL_CONFIG = {
        'user': os.getenv('MYSQL_USER'),
        'passwd': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT')),
        'db': os.getenv('MYSQL_DB'),
        'charset': 'utf8'
    }

    @classmethod
    def validate_credentials(cls):
        missing_credentials = []

        # Check for missing Elasticsearch credentials
        for key, value in cls.ES_CONFIG.items():
            if not value:
                missing_credentials.append(f"Missing Elasticsearch credential: {key}")

        # Check for missing MySQL credentials
        for key, value in cls.MYSQL_CONFIG.items():
            if not value:
                missing_credentials.append(f"Missing MySQL credential: {key}")

        if missing_credentials:
            raise ValueError("Configuration Error: " + "; ".join(missing_credentials))


Config.validate_credentials()


class DatalakeConnection(Datalake):
    def __init__(self):
        super().__init__()

        ES_CONFIG = Config.ES_CONFIG
        ES_CONFIG['connection_type'] = 'es'

        MYSQL_CONFIG = Config.MYSQL_CONFIG
        MYSQL_CONFIG['connection_type'] = 'sql'

        self.plotch_pipeline = self.create_pipeline(name="groclake_pipeline")
        self.plotch_pipeline.add_connection(name="es_connection", config=ES_CONFIG)
        self.plotch_pipeline.add_connection(name="sql_connection", config=MYSQL_CONFIG)

        self.execute_all()

        self.connections = {
            "es_connection": self.get_connection("es_connection"),
            "sql_connection": self.get_connection("sql_connection")
        }

    def get_connection(self, connection_name):
        """
        Returns a connection by name from the pipeline.
        """
        return self.plotch_pipeline.get_connection_by_name(connection_name)


datalake_connection = DatalakeConnection()
es_connection = datalake_connection.connections["es_connection"]
mysql_connection = datalake_connection.connections["sql_connection"]


class Joblake:

    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError('Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
        self.index_uuid = index_uuid

    def generate_unique_id(self, length=16):
        characters = string.ascii_lowercase + string.digits
        unique_id = ''.join(random.choices(characters, k=length))
        return unique_id

    def get_current_datetime(self) -> str:
        return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    def get_existing_index_uuid(self, index_uuid, entity_type):
        condition_clause = "entity_id = %s AND entity_type= %s"
        query = f"SELECT * FROM groclake_entity_master WHERE {condition_clause}"
        params = (index_uuid, entity_type)
        result = mysql_connection.read(query, params, multiple=False)
        return result

    def save_joblake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, joblake_name=None):

        if joblake_name:
            joblake_name = joblake_name

        if not joblake_name:
            return {"message": "Joblake name is required. Please provide a valid joblake name"}
        if not joblake_name.lower().strip().isidentifier():
            return {'error': f'Invalid Joblake name. Only alphanumeric characters and underscores are allowed.'}

        if not self.index_uuid:
            self.index_uuid = self.generate_unique_id()

        existing_data = self.get_existing_index_uuid(self.index_uuid,'joblake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid=existing_data.get('entity_id')
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id', ''),
                "joblake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": f"jb_{self.index_uuid}",
            "entity_type": 'joblake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": joblake_name
        }
        try:
            response = es_connection.create_index(f"jb_{self.index_uuid}", settings=None, mappings=joblake_mapping)
            self.index_uuid=f"jb_{self.index_uuid}"
        except Exception as es_error:
            return {"message": "Elasticsearch error occurred while creating Joblake.", "error": str(es_error)}
        try:
            self.save_joblake_data_in_db(db_params, 'groclake_entity_master')
        except Exception as db_error:
            return {"message": "Database error occurred while saving Joblake.", "error": str(db_error)}
        return {
            "message": "JobLake created successfully",
            "index_uuid": f"jb_{self.index_uuid}",
            "joblake_name":joblake_name
        }
