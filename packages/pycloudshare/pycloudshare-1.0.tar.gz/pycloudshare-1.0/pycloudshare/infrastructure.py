from pycloudshare.utils import load_api_vars
from pycloudshare.accelerate import CloudShareAccelerate
from pycloudshare.classic import CloudShareClassic

class Infrastructure:

    def __init__(self):
        self.api_vars = load_api_vars()
        self.project_id = self.api_vars['CLOUDSHARE_PROJECT_ID']
        self.csa = CloudShareAccelerate()
        self.csc = CloudShareClassic()

    def _get_project_training_experiences(self):

        '''Example helper method to get all training experiences for a project.'''

        all_training_experiences = self.csa.get_trainings_experiences()['items']
        project_training_experiences = []
        for training_experience in all_training_experiences:
            if training_experience['projectId'] == self.project_id:
                project_training_experiences.append(training_experience)
        return project_training_experiences

    def load_modules(self):

        '''Example method to load all training experiences as what we defined
            as "Modules".'''

        return self._get_project_training_experiences()

    def load_module(self, room_id):

        '''Example method to load a training experience as what we defined
            as a "Module".'''

        return self.csa.get_training_experience(room_id)

    def build_room_link(self, room_id, first_name, last_name, email):

        '''Example contextual method to build a sponsored link for what we
            defined as a "Module"'''

        link_dict =  self.csa.create_sponsored_link_for_training(training_id=room_id,
                                                                 first_name=first_name,
                                                                 last_name=last_name,
                                                                 email=email)
        return link_dict['loginUrl']

    def get_learning_path_modules(self, path_id):

        '''Example contextual method to get all rooms in a what we defined
            as a "Learning Path"'''

        project_training_experiences = self._get_project_training_experiences()
        path_modules = []
        for training_experience in project_training_experiences:
            labels = training_experience['labels']
            for label in labels:
                label_id = int(label.split('_')[-1])
                if label_id == path_id:
                    path_modules.append(training_experience)
                    break
        return path_rooms
