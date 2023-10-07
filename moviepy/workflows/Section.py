import abc

# An abstract base class for sections
# Once your video has been split into sections, you can act on the information 
# provided from each sectioned video clip
class Section(abc.ABC):
    def __init__(self, sectionedVideos):
        self.videos = sectionedVideos # Your list of sectioned video clips

    # A user defined method for determining the template that your sectioned video clips should use
    # Often will result in the creation of custom templates; the provided
    @abc.abstractmethod
    def determineTemplate(self): 
        pass