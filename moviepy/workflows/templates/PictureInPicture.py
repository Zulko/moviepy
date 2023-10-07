# What the base templates would do is provide support
# to make the determineTemplate function easier to create
from moviepy.workflows.Template import BaseTemplate
# Extend class
class PictureInPicture(BaseTemplate):
    def __init__(self, videos):
        super().__init__(videos)

    # TODO: implement methods to customize video parameters
    # 
    def setOrientations():
        raise NotImplementedError
    def setAudioFX():
        raise NotImplementedError
    def setVideoFX():
        raise NotImplementedError

# Instantiate template
# In the case of picture_in_picture, a picture_in_picture setup would be created
# TODO
# picture_in_picture = BaseTemplate()