

class ProjectImageNotFoundError(Exception):
    def __init__(self, project_image_id):
        self.project_image_id = project_image_id
        self.message = f"A project image with the id '{self.project_image_id}' does not exist."
        super().__init__(self.message)



class DuplicateProjectImageDisplayOrderError(Exception):
    def __init__(self, project_image_display_order, project_id):
        self.project_image_display_order = project_image_display_order
        self.project_id = project_id
        self.message = f"Display order '{self.project_image_display_order}' already exists for project {self.project_id}."
        super().__init__(self.message)