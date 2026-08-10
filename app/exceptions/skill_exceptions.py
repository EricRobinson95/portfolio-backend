
class DuplicateSkillNameError(Exception):
    def __init__(self, name):
        self.name = name
        self.message = f"A skill with the name '{self.name}' already exists."
        super().__init__(self.message)

class SkillNotFoundError(Exception):
    def __init__(self, skill_id):
        self.skill_id = skill_id
        self.message = f"Skill with ID {self.skill_id} does not exist."
        super().__init__(self.message)
