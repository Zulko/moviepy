from moviepy.workflows.Section import Section
# Implements abstract Section class
class MusicSection(Section): 
    def __init__(self, videos):
        super().__init__(videos)

    # TODO: write my code to determine which template to use based on videos here
    def determineTemplate(self):
        raise NotImplementedError