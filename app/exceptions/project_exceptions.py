
class DuplicateProjectTitleError(Exception):
    def __init__(self, title):
        self.title = title
        self.message = f"A project with the title '{self.title}' already exists."
        super().__init__(self.message)

class ProjectNotFoundError(Exception):
    def __init__(self, project_id):
        self.project_id = project_id
        self.message = f"Project with ID {self.project_id} does not exist."
        super().__init__(self.message)