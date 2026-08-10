


class ProjectTechnologyAlreadyExistsError(Exception):
    def __init__(self, project_id, technology_id):
        self.project_id = project_id
        self.technology_id = technology_id
        self.message = f"Technology with ID {self.technology_id} is already assigned to project ID {self.project_id}."
        super().__init__(self.message)

class ProjectTechnologyNotFoundError(Exception):
    def __init__(self, project_id, technology_id):
        self.project_id = project_id
        self.technology_id = technology_id
        self.message = f"Technology with ID {self.technology_id} is not assigned to project ID {self.project_id}."
        super().__init__(self.message)

