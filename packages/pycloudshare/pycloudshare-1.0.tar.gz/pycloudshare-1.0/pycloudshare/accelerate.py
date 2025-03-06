import requests
import logging
from pycloudshare.utils import load_api_vars

class CloudShareAccelerate:

    def __init__(self):
        self.api_vars = load_api_vars()
        self.api_id = self.api_vars['CLOUDSHARE_API_ID']
        self.api_key = self.api_vars['CLOUDSHARE_API_KEY']
        self.api_url = self.api_vars['CLOUDSHARE_ACCELERATE_API_URL']
        self.access_token = None
        self._update_access_token()

    def _get_access_token(self):
        oauth_token_url = f'{self.api_url}oauth/token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.api_id,
            'client_secret': self.api_key
        }
        response = requests.post(oauth_token_url, data=payload)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            logging.debug('Access token obtained successfully')
        else:
            access_token = None
            logging.error(f'Failed to obtain access token: {response.text}')
        return access_token

    def _update_access_token(self):
        logging.debug('Updating access token')
        self.access_token = self._get_access_token()

    def _interact(self, method, path, content=None, params=None):
        method = method.upper().strip()
        full_url = f'{self.api_url}{path}'
        logging.debug(f'Interacting with {method} {full_url}')
        self._update_access_token()
        if not self.access_token:
            logging.error('No access token available.')
            return None
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request(
                method=method,
                url=full_url,
                headers=headers,
                json=content,
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f'Error {response.status_code}: {response.text}')
                return None
        except requests.RequestException as e:
            logging.error(f'HTTP Request failed: {e}')
            return None

    # Trainings
    def get_trainings_experiences(self):
        """Get Training Experience List"""
        return self._interact('GET', 'trainings')

    def create_training_experience(self, data):
        """Create Training Experience"""
        return self._interact('POST', 'trainings', content=data)

    def get_training_experience(self, training_id):
        """Get Training Experience by ID"""
        return self._interact('GET', f'trainings/{training_id}')

    # Instructors
    def add_instructor_to_training(self, training_id, data):
        """Add Instructor to a Training Experience"""
        return self._interact('POST', f'trainings/{training_id}/instructors', content=data)

    def get_instructors_in_training(self, training_id):
        """Get List of Instructors in a Training Experience"""
        return self._interact('GET', f'trainings/{training_id}/instructors')

    def invite_instructors_to_training(self, training_id, data):
        """Invite Instructors to a Training Experience"""
        return self._interact('POST', f'trainings/{training_id}/instructors/invite', content=data)

    # Students
    def get_students_in_training(self, training_id):
        """Get List of Students in a Training Experience"""
        return self._interact('GET', f'trainings/{training_id}/students')

    def add_students_to_training(self, training_id, data):
        """Add Students to a Training Experience"""
        return self._interact('POST', f'trainings/{training_id}/students', content=data)

    def invite_students_to_training(self, training_id, data):
        """Invite Students to a Training Experience"""
        return self._interact('POST', f'trainings/{training_id}/students/invite', content=data)

    # Sponsored Link
    def create_sponsored_link_for_training(self, training_id, first_name, last_name, email):
        """Create Sponsored Link for a Training Experience"""
        data = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email
        }
        return self._interact('POST', f'trainings/{training_id}/sponsored-link', content=data)
