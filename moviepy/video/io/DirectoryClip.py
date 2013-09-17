from moviepy.video.VideoClip import VideoClip

class DirectoryClip(VideoClip):
    """
    
    A VideoClip read from a directory containing pictures.
    Still experimental and subject to changes.
    
    DEPRECATED - needs update
    
    """

    def __init__(self, foldername, fps, transparent=True, ismask=False):

        VideoClip.__init__(self, ismask=ismask)

        self.directory = foldername
        self.fps = fps
        allfiles = os.listdir(foldername)
        self.pics = sorted(["%s/%s" % (foldername, f) for f in allfiles
                            if not f.endswith(('.txt','.wav'))])
        
        audio = [f for f in allfiles if f.endswith('.wav')]
        
        if len(audio) > 0:
            self.audio = AudioFileClip(audio[0])
            self.audiofile =audio[0]

        self.size = imread(self.pics[0]).shape[:2][::-1]

        if imread(self.pics[0]).shape[2] == 4:  # transparent png

            if ismask:
                def get_frame(t):
                    return 1.0 * imread(self.pics[int(self.fps * t)])[:, :, 3] / 255
            else:
                def get_frame(t):
                    return imread(self.pics[int(self.fps * t)])[:, :, :2]

            if transparent:
                self.mask = DirectoryClip(foldername, fps, ismask=True)

        else:

            def get_frame(t):
                return imread(self.pics[int(self.fps * t)])

        self.get_frame = get_frame
        self.duration = 1.0 * len(self.pics) / self.fps

    def to_videofile(self, filename, bitrate=3000, audio=True):
        """
        Transforms the directory clip into a movie using ffmpeg.
        Uses the framerate specified by ``clip.fps``.
        
        :param filename: name of the video file to write in, like
            'myMovie.ogv' or 'myFilm.mp4'.
        :param bitrate: final bitrate of the video file (in kilobytes/s).
            3000-6000 gives generally light files and an acceptable quality.
        :param audio: the name of an audiofile to be incorporated in the
           the movie.
        """

        if audio != None:
            # if there is audio, then ``videofile`` is a temporary file
            # that will then be merged with audio and removed.
            name, ext = os.path.splitext(os.path.basename(filename))
            videofile = Clip._TEMP_FILES_PREFIX + name + ext
        else:
            videofile = filename
            
        cmd = ["ffmpeg", "-y", "-f", "image2",
              "-r","%d"%self.fps,
              "-i", os.path.join(self.directory,self.directory,"%06d.png"),
              "-b", "%dk"%bitrate,
              "-r", "%d"%self.fps, videofile]
         
        print "running : "+ " ".join(cmd)
        subprocess.call(cmd)

        if audio:
            # Merge video and audio, and remove temporary files
            subprocess.call(["ffmpeg", "-y",
                        "-i", self.audiofile +
                        "-i", videofile,
                        "-strict experimental", filename])
             
            print "running:  %s" % cmd
            os.system(cmd)
            os.remove(videofile)
