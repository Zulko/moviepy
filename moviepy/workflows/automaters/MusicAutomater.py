from moviepy.workflows.Automater import Automater
# Implements abstract Automater class
class MusicAutomater(Automater): 
    def __init__(self, videos):
        super().__init__(videos)

    # TODO: write my code to determine music vid sections based on the vid input here
    def determineSections(self):
        raise NotImplementedError