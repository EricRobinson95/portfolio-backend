


class ProjectSkillAlreadyExistsError(Exception):
    def __init__(self, project_id, skill_id):
        self.project_id = project_id
        self.skill_id = skill_id
        self.message = f"Skill with ID {self.skill_id} is already assigned to project ID {self.project_id}."
        super().__init__(self.message)

class ProjectSkillNotFoundError(Exception):
    def __init__(self, project_id, skill_id):
        self.project_id = project_id
        self.skill_id = skill_id
        self.message = f"Skill with ID {self.skill_id} is not assigned to project ID {self.project_id}."
        super().__init__(self.message)

