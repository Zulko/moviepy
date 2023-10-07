# What the base templates would do is provide support
# to make the determineTemplate function easier to create
from moviepy.workflows.Template import BaseTemplate
# Extend class
class Title(BaseTemplate):
    # TODO: extend BaseTemplate in title class
    def __init__(self, videos, orientationFunction, audioFXFunction, videoFXFunction):
        super().__init__(videos, orientationFunction, audioFXFunction, videoFXFunction)
    

# Instantiate extended class 
# In the case of title, some sort of title screen would be created
# TODO
# title = Title()