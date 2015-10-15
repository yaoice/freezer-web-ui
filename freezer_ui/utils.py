# Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import uuid


import datetime
from django.template.defaultfilters import date as django_date


def create_dict_action(**kwargs):
    """Create a dict only with values that exists so we avoid send keys with
    None values
    """
    return {k: v for k, v in kwargs.items() if v}


def timestamp_to_string(ts):
    return django_date(
        datetime.datetime.fromtimestamp(int(ts)),
        'SHORT_DATETIME_FORMAT')


class Dict2Object(object):
    """Makes dictionary fields accessible as if they are attributes.

    The dictionary keys become class attributes. It is possible to use one
    nested dictionary by overwriting nested_dict with the key of that nested
    dict.

    This class is needed because we mostly deal with objects in horizon (e.g.
    for providing data to the tables) but the api only gives us json data.
    """
    nested_dict = None

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __getattr__(self, attr):
        """Make data_dict fields available via class interface """
        if attr in self.data_dict:
            return self.data_dict[attr]
        elif attr in self.data_dict[self.nested_dict]:
            return self.data_dict[self.nested_dict][attr]
        else:
            return object.__getattribute__(self, attr)

    def get_dict(self):
        return self.data_dict


class Action(Dict2Object):
    nested_dict = 'job_action'

    @property
    def id(self):
        return self.job_id


class Job(Dict2Object):
    nested_dict = 'job_actions'

    @property
    def id(self):
        return self.job_id


class Backup(Dict2Object):
    nested_dict = 'backup_metadata'

    @property
    def id(self):
        return self.backup_id


class Client(object):
    def __init__(self, uuid, hostname, client_id):
        self.uuid = uuid
        self.hostname = hostname
        self.client_id = client_id


class ActionJob(object):
    def __init__(self, job_id, action_id, action, backup_name):
        self.job_id = job_id
        self.action_id = action_id
        self.action = action
        self.backup_name = backup_name


class Session(object):
    def __init__(self, session_id, description, status, jobs,
                 start_datetime, interval, end_datetime):
        self.session_id = session_id
        self.description = description
        self.status = status
        self.jobs = jobs
        self.start_datetime = start_datetime
        self.interval = interval
        self.end_datetime = end_datetime


class SessionJob(object):
    """Create a job object to work with in horizon"""
    def __init__(self, job_id, session_id, client_id, status):
        self.job_id = job_id
        self.session_id = session_id
        self.client_id = client_id
        self.status = status


class JobList(object):
    """Create an object to be passed to horizon tables that handles
    nested values
    """
    def __init__(self, description, result, job_id):
        self.description = description
        self.result = result
        self.id = job_id
        self.job_id = job_id


def create_dummy_id():
    """Generate a dummy id for documents generated by the scheduler.

    This is needed when the scheduler creates jobs with actions attached
    directly, those actions are not registered in the db.
    """
    return uuid.uuid4().hex


def actions_in_job(ids):
    """Return an ordered list of actions for a new job
    """
    ids = ids.split('===')
    return [i for i in ids if i]


def assign_value_from_source(source_dict, dest_dict, key):
    """Assign a value to a destination dict from a source dict
    if the key exists
    """
    if key in source_dict:
        dest_dict[key] = source_dict.pop(key)
