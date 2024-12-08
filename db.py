
import boto3
from logger_setup import setup_logger
import os
import uuid
from datetime import datetime, timezone
import random
import yaml
from decimal import Decimal
from dotenv import load_dotenv
import logging
from typing import Literal
from config import Config

# boto3.set_stream_logger('botocore', level=logging.DEBUG)

'''
Schema
===

PARTICIPANT#PartID, PARTICIPANT#Timestamp
PARTICIPANT#PartID, MSG#MsgID: role, content, state
PARTICIPANT#PartID, ISSUE#IssueType#TEXT: issue_text, ts
PARTICIPANT#PartID, ISSUE#IssueType#NEG: neg_emo, ts
PARTICIPANT#PartID, ISSUE#IssueType#POS: pos_emo, ts
PARTICIPANT#PartID, REAPS#IssueType#ReapNum#TEXT: reap_text, ts
PARTICIPANT#PartID, REAPS#IssueType#ReapNum#RANK: reap_rank, ts
PARTICIPANT#PartID, REAPS#IssueType#ReapNum#SUCCESS: reap_success, ts
PARTICIPANT#PartID, REAPS#IssueType#ReapNum#BELIEVABILITY: reap_believability, ts
PARTICIPANT#PartID, SURVEY#SurveyType#ItemNum: value, ts

PartID = prolific id
MsgID = unix timestamp
IssueType = career | relationship

'''

logger = setup_logger()
load_dotenv()


aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_DEFAULT_REGION')


config = Config()

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

table = dynamodb.Table(config.dynamo_tbl_name)

def db_add_message(pid: str, role: Literal['user', 'assistant'], content: str, state: str, domain: Literal['CAREER', 'RELATIONSHIP']):
    '''
    Adds a message to the database
    '''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(
        Item={
            'PK': f'PARTICIPANT#{pid}',
            'SK': f'MSG#{timestamp}',
            'role': role,
            'content': content,
            'ts': timestamp,
            'state': state,
            'domain': domain
        }
    )

def db_new_participant(pid: str):
    '''
    Adds a new participant to the database
    '''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(
        Item={
            'PK': f'PARTICIPANT#{pid}',
            'SK': f'PARTICIPANT#{timestamp}',
            'ts': timestamp
        }
    )

def db_issue_feature(pid: str, issue_type: Literal['CAREER', 'RELATIONSHIP'], feature_type: Literal['NEG', 'POS', 'SUMMARY'], value):
    '''
    Adds a new issue emotion to the database
    '''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(
        Item={
            'PK': f'PARTICIPANT#{pid}',
            'SK': f'ISSUE#{issue_type.upper()}#{feature_type.upper()}',
            'value': value,
            'ts': timestamp
        }
    )

def db_new_reap(pid: str, issue_type: Literal['CAREER', 'RELATIONSHIP'], reap_num: int, reap_text: str):
    '''
    Adds a new reappraisal to the database
    '''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(
        Item={
            'PK': f'PARTICIPANT#{pid}',
            'SK': f'REAPS#{issue_type.upper()}#{reap_num}#TEXT',
            'reap_text': reap_text,
            'ts': timestamp
        }
    )

def db_reap_feature(pid: str, issue_type: Literal['CAREER', 'RELATIONSHIP'], reap_num: int, feature_type: Literal['SUCCESS', 'BELIEVABLE', 'VALUES'], value):
    '''
    Adds a new reap feature to the database
    '''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.put_item(
        Item={
            'PK': f'PARTICIPANT#{pid}',
            'SK': f'REAPS#{issue_type.upper()}#{reap_num}#{feature_type.upper()}',
            'value': value,
            'ts': timestamp
        }
    )

# def db_survey_item(pid: str, survey_type: Literal['values', 'beliefs'], item_num: int, value):
#     '''
#     Adds a new survey item to the database
#     '''
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     table.put_item(
#         Item={
#             'PK': f'PARTICIPANT#{pid}',
#             'SK': f'SURVEY#{survey_type.upper()}#{item_num}',
#             'value': value,
#             'ts': timestamp
#         }
#     )
    
