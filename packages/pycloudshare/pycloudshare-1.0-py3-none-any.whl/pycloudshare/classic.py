import cloudshare as cs
import logging
from pycloudshare.utils import load_api_vars

class CloudShareClassic:

    def __init__(self):
        self.api_vars = load_api_vars()
        self.api_id = self.api_vars['CLOUDSHARE_API_ID']
        self.api_key = self.api_vars['CLOUDSHARE_API_KEY']
        self.api_hostname = self.api_vars['CLOUDSHARE_API_HOSTNAME']

    def _interact(self, method, path, content=None, params=None):
        method = method.upper().strip()
        logging.debug(f'Interacting with {method} {path}')
        if params:
            query_string = '&'.join(f"{key}={value}" for key, value in params.items())
            if '?' in path:
                path += '&' + query_string
            else:
                path += '?' + query_string
        res = cs.req(
            hostname=self.api_hostname,
            method=method,
            path=path,
            apiId=self.api_id,
            apiKey=self.api_key,
            content=content
        )
        if res.status == 200:
            return res.content
        else:
            # Handle errors
            logging.error(f"Error {res.status}: {res.content}")
            return None

    # Projects
    def get_projects(self, filter_criteria=None):
        path = 'projects'
        if filter_criteria:
            path += f'/{filter_criteria}'
        return self._interact('GET', path)

    def get_project(self, project_id):
        path = f'projects/{project_id}'
        return self._interact('GET', path)

    # Blueprints
    def get_blueprints_for_project(self, project_id):
        path = f'projects/{project_id}/blueprints'
        return self._interact('GET', path)

    def get_blueprint(self, project_id, blueprint_id):
        path = f'projects/{project_id}/blueprints/{blueprint_id}'
        return self._interact('GET', path)

    # Policies
    def get_policies_for_project(self, project_id):
        path = f'projects/{project_id}/policies'
        return self._interact('GET', path)

    # Classes
    def get_classes(self):
        path = 'class'
        return self._interact('GET', path)

    def get_class(self, class_id):
        path = f'class/{class_id}'
        return self._interact('GET', path)

    def get_class_details(self):
        path = 'class/actions/getdetailed'
        return self._interact('GET', path)

    def create_class(self, data):
        path = 'class'
        return self._interact('POST', path, content=data)

    def update_class(self, data):
        path = 'class'
        return self._interact('PUT', path, content=data)

    def delete_class(self, class_id):
        path = f'class/{class_id}'
        return self._interact('DELETE', path)

    # Class Actions
    def get_class_countries(self):
        path = 'class/actions/countries'
        return self._interact('GET', path)

    def get_class_instructors(self):
        path = 'class/actions/instructors'
        return self._interact('GET', path)

    def get_class_custom_fields(self):
        path = 'class/actions/customfields'
        return self._interact('GET', path)

    def send_class_invitations(self, data):
        path = 'class/actions/sendinvitations'
        return self._interact('POST', path, content=data)

    def suspend_all_class_environments(self, data):
        path = 'class/actions/suspendallenvironments'
        return self._interact('PUT', path, content=data)

    def resume_all_class_environments(self, class_id):
        path = f'class/{class_id}/students/actions/resumeenvironmentforstudent'
        return self._interact('POST', path)

    def delete_all_class_environments(self, data):
        path = 'class/actions/deleteallenvironments'
        return self._interact('DELETE', path, content=data)

    def create_class_sponsored_link(self, data):
        path = 'class/sponsoredlink'
        return self._interact('POST', path, content=data)

    def disable_class_sponsored_link(self, data):
        path = 'class/disablesponsoredlink'
        return self._interact('POST', path, content=data)

    # Students
    def get_class_students(self, class_id):
        path = f'class/{class_id}/students'
        return self._interact('GET', path)

    def get_class_student(self, class_id, student_id):
        path = f'class/{class_id}/students/{student_id}'
        return self._interact('GET', path)

    def register_student(self, class_id, data):
        path = f'class/{class_id}/students'
        return self._interact('POST', path, content=data)

    def update_student(self, class_id, student_id, data):
        path = f'class/{class_id}/students/{student_id}'
        return self._interact('PUT', path, content=data)

    def remove_student(self, class_id, student_id):
        path = f'class/{class_id}/students/{student_id}'
        return self._interact('DELETE', path)

    # Instructors
    def get_instructors_in_class(self, class_id):
        path = 'instructors/class'
        params = {'classId': class_id}
        return self._interact('GET', path, params=params)

    def add_instructor(self, data):
        path = 'instructors'
        return self._interact('POST', path, content=data)

    def remove_instructor(self, instructor_id):
        path = f'instructors/{instructor_id}'
        return self._interact('DELETE', path)

    # Ping
    def ping(self):
        path = 'ping'
        return self._interact('GET', path)

    # Regions
    def get_regions(self):
        path = 'regions'
        return self._interact('GET', path)

    # Timezones
    def get_timezones(self):
        path = 'timezones'
        return self._interact('GET', path)

    # Environments
    def get_environments(self):
        path = 'envs'
        return self._interact('GET', path)

    def get_environment(self, env_id):
        path = f'envs/{env_id}'
        return self._interact('GET', path)

    def get_environment_resources(self, env_id):
        path = 'envs/actions/getenvresources'
        params = {'envId': env_id}
        return self._interact('GET', path, params=params)

    def get_multiple_environments_resources(self, params):
        path = 'envs/actions/getmultipleenvsresources'
        return self._interact('GET', path, params=params)

    def get_environment_extended(self, env_id):
        path = 'envs/actions/getextended'
        params = {'envId': env_id}
        return self._interact('GET', path, params=params)

    def get_environment_extended_by_token(self, token):
        path = 'envs/actions/getextendedbytoken'
        params = {'token': token}
        return self._interact('GET', path, params=params)

    def get_environment_by_machine_vanity(self, vanity_name):
        path = 'envs/actions/getextendedbymachinevanity'
        params = {'vanityName': vanity_name}
        return self._interact('GET', path, params=params)

    def delete_environment(self, env_id):
        path = f'envs/{env_id}'
        return self._interact('DELETE', path)

    def create_environment(self, data):
        path = 'envs'
        return self._interact('POST', path, content=data)

    def add_vms_to_environment(self, data):
        path = 'envs'
        return self._interact('PUT', path, content=data)

    def suspend_environment(self, data):
        path = 'envs/actions/suspend'
        return self._interact('PUT', path, content=data)

    def resume_environment(self, data):
        path = 'envs/actions/resume'
        return self._interact('PUT', path, content=data)

    def extend_environment(self, data):
        path = 'envs/actions/extend'
        return self._interact('PUT', path, content=data)

    def revert_environment(self, data):
        path = 'envs/actions/revert'
        return self._interact('PUT', path, content=data)

    def postpone_environment_inactivity(self, data):
        path = 'envs/actions/postponeinactivity'
        return self._interact('PUT', path, content=data)

    # VMs
    def delete_vm(self, vm_id):
        path = f'vms/{vm_id}'
        return self._interact('DELETE', path)

    def revert_vm(self, data):
        path = 'vms/actions/revert'
        return self._interact('PUT', path, content=data)

    def reboot_vm(self, data):
        path = 'vms/actions/reboot'
        return self._interact('PUT', path, content=data)

    def edit_vm_hardware(self, data):
        path = 'vms/actions/editvmhardware'
        return self._interact('PUT', path, content=data)

    def execute_command_on_vm(self, data):
        path = 'vms/actions/executepath'
        return self._interact('POST', path, content=data)

    def check_execution_status(self, data):
        path = 'vms/actions/checkexecutionstatus'
        return self._interact('PUT', path, content=data)

    def get_remote_access_file(self, params):
        path = 'vms/actions/getremoteaccessfile'
        return self._interact('GET', path, params=params)

    # Cloud Folders
    def get_cloud_folders(self):
        path = 'cloudfolders/actions/getall'
        return self._interact('GET', path)

    def mount_cloud_folder(self, data):
        path = 'actions/mount'
        return self._interact('PUT', path, content=data)

    def unmount_cloud_folder(self, data):
        path = 'actions/unmount'
        return self._interact('PUT', path, content=data)

    def regenerate_cloud_folder_password(self):
        path = 'actions/regeneratecloudfolderspassword'
        return self._interact('PUT', path)

    # Templates
    def get_templates(self):
        path = 'templates'
        return self._interact('GET', path)

    # Snapshots
    def get_snapshot(self, snapshot_id):
        path = f'snapshots/{snapshot_id}'
        return self._interact('GET', path)

    def get_snapshots_for_environment(self, env_id):
        path = 'snapshots/actions/getforenv'
        params = {'envId': env_id}
        return self._interact('GET', path, params=params)

    def mark_snapshot_as_default(self, data):
        path = 'snapshots/actions/markdefault'
        return self._interact('PUT', path, content=data)

    def take_snapshot(self, data):
        path = 'snapshots/actions/takesnapshot'
        return self._interact('POST', path, content=data)

    # Invitations
    def get_invitation_options(self):
        path = 'invitations'
        return self._interact('OPTIONS', path)

    def invite_to_poc(self, data):
        path = '/api/../invitetopoc'
        return self._interact('POST', path, content=data)

    def invite_project_member(self, data):
        path = 'invitations/actions/inviteprojectmember'
        return self._interact('POST', path, content=data)

    # Sponsored Links
    def get_sponsored_links_options(self):
        path = 'sponsoredlinks'
        return self._interact('OPTIONS', path)

    def create_sponsored_link(self, data):
        path = 'sponsoredlinks'
        return self._interact('POST', path, content=data)

    # Teams
    def get_teams(self):
        path = 'teams'
        return self._interact('GET', path)

    # Users
    def get_login_url(self):
        path = 'users/actions/getloginurl'
        return self._interact('GET', path)

    def get_replacing_users_options(self, data):
        path = 'users/actions/GetReplacingUsersOptions'
        return self._interact('POST', path, content=data)

    def remove_user_role(self, data):
        path = 'users/actions/RemoveUserRole'
        return self._interact('POST', path, content=data)

    # Webhooks
    def get_webhooks(self):
        path = 'webhooks'
        return self._interact('GET', path)

    def get_webhook(self, webhook_id):
        path = f'webhooks/{webhook_id}'
        return self._interact('GET', path)

    def create_webhook(self, data):
        path = 'webhooks'
        return self._interact('POST', path, content=data)

    def delete_webhook(self, webhook_id):
        path = f'webhooks/{webhook_id}'
        return self._interact('DELETE', path)

    # External Clouds
    def get_external_cloud_env(self, environment_id):
        path = f'externalclouds/ervins/{environment_id}'
        return self._interact('GET', path)

    def get_external_clouds_vms(self, environment_id):
        path = f'externalCloudsVms/{environment_id}'
        return self._interact('GET', path)
