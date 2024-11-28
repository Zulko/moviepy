from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# An abstract parent class for templates
# Templates provide a powerful way to approach video editing, 
# taking sections and automatically creating a video based on the information
# encoded in the section and the template.
# This is where the real magic happens, taking a list of sectioned videos and
# turning them into one edited section of a video.   
# Templates apply orientation and fx to clips in an organized manner
# This is a base class for templates that can be extended via inheritance
class BaseTemplate():
    def __init__(self, videos, orientationFunction=lambda: None, audioFXFunction=lambda: None, videoFXFunction=lambda: None):
        self.videos = videos
        self.orientationFunction = orientationFunction
        self.audioFXFunction = audioFXFunction
        self.videoFXFunction = videoFXFunction

    # Sets the orientation of each sectioned video
    def setOrientations(self):
        self.orientationFunction()
    # Sets the audio fx of each sectioned video
    def setAudioFX(self): 
        self.audioFXFunction()
    # Sets the video fx of each sectioned video
    def setVideoFX(self): 
        self.videoFXFunction()

    # renders the video given the current template information 
    # shows the user the template and then returns it for further customized editing
    def renderVideo(self):
        # composite template
        template = CompositeVideoClip([video for video in self.videos])
        # preview template 
        template.preview()
        # return template
        return template