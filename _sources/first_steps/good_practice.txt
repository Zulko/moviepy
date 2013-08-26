.. _goodPractices:

Good Practices
---------------

MoviePy works fine on my 1.5 petaflops supercomputer, but like for any other video software, the bottleneck is the heavy computations required to produce several pictures per second. If you write a very complex clip, the previews and the rendering to a file may be very slow. Here are a few tricks to ease things:


- Use an interactive shell, like IPython or, better, the IPython notebook. If you don't know these, you don't know what you are missing !
- Prefer the clip.show() option, and use it a lot. Only use clip.preview() when really necessary.
- For the moment the audio is generated for each preview and before the preview. So if you want to preview a lengthy clip with sound, it may take a few seconds before the preview actually launches, and the sound may take lots of place in memory. Therefore, it is advised to only preview small bits of a movie with audio. Reducing the audio fps when previewing reduces the problem. 
- If some part of your video is particularly complex and long to render, save this part as either a raw video (enables to save the sound) or in a directory of pictures (enables to save the mask), then use this video instead of this part's script. ::
      
      myVideo.to_movie('save.avi',fps=24,codec='raw', audio=True)
      # or
      myVideo.to_directory('./mySaveDirectory',fps=24)
      
- If you are going to use extracts of big movies with sound, do NOT write ::
      
      # "Charade" is a 2h00 long movie
      myVideo = MovieClip("charade.mp4",sound=True).subclip(30,35)
      
  The reason is that in the snippet above the whole sound of the movie will be converted into a .wav file and then loaded into the memory. Instead, extract the subclip  between t=30s and t=35s as a new video file and use this one instead. Like this ::
  
      import moviepy.ffmpeg as mf
      mf.extract_subclip("charade.mp4",30,35, "charadeSUB30_35.mp4")
      myVideo = MovieClip("charadeSUB30_35.mp4",sound=True)
      
- Prototype: design your clips separately. If your composition involves a clip that is not finished yet, replace it temporarily with a basic color clip.
- There are often several ways to produce a same effect with MoviePy, but some ways are faster. For instance don't apply effects to a whole screen video if you are only using one region of the screen afterwards: first crop the selected region, then apply your effects.
- [wishful thinking] Check on the internet or in the examples of this documentation that what you do hasn't been done before. Code shared on the internet has more chances to be optimized.
