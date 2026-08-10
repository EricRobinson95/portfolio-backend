
class DuplicateTechnologyNameError(Exception):
    def __init__(self, name):
        self.name = name
        self.message = f"A technology with the name '{self.name}' already exists."
        super().__init__(self.message)

class TechnologyNotFoundError(Exception):
    def __init__(self, technology_id):
        self.technology_id = technology_id
        self.message = f"Technology with ID {self.technology_id} does not exist."
        super().__init__(self.message)
