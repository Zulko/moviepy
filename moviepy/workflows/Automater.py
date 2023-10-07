import abc

# An abstract base class for automation
# The idea is you can create custom Automater classes that take videos as parameters
# and implement a method where you can automate the splitting of your video into sections
class Automater(abc.ABC): 
    def __init__(self, videos):
        self.videos = videos # Your list of full video clips

    # A method for the user to implement
    # Provides time data to automates the splitting of your video into sections
    # using the sectionVideos function
    @abc.abstractmethod
    def determineSections(self):
        pass

    # Returns a list of sectioned videos dependent on the output of determineSections
    def sectionVideos(videoTimeData):
        videos = []
        # Iterate over key values
        for video, time in videoTimeData: 
            videos.append(video.cutout(time[0], time[1])) # Cut the video out based on the time interval
        return videos
