
Working with `matplotlib`
=========================

Defining custom animations
~~~~~~~~~~~~~~~~~~~~~~~~~~

MoviePy allows you to produce custom animations by defining a function that returns a frame at a given time of the animation in the form of a numpy array.

An example of this workflow is below: ::

	from moviepy.editor import VideoClip

	def make_frame(t):
	    """Returns an image of the frame for time t."""
	    # ... create the frame with any library here ...
	    return frame_for_time_t # (Height x Width x 3) Numpy array

	animation = VideoClip(make_frame, duration=3) # 3-second clip

This animation can then be exported by the usual MoviePy means: ::

	# export as a video file
	animation.write_videofile("my_animation.mp4", fps=24)
	# export as a GIF
	animation.write_gif("my_animation.gif", fps=24) # usually slower

Simple `matplotlib` example
~~~~~~~~~~~~~~~~~~~~~~~~~~~

An example of an animation using `matplotlib` can then be as follows: ::

	import matplotlib.pyplot as plt
	import numpy as np
	from moviepy.editor import VideoClip
	from moviepy.video.io.bindings import mplfig_to_npimage

	x = np.linspace(-2, 2, 200) 

	duration = 2

	fig, ax = plt.subplots()
	def make_frame(t):
	    ax.clear()
	    ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
	    ax.set_ylim(-1.5, 2.5)
	    return mplfig_to_npimage(fig)
	    
	animation = VideoClip(make_frame, duration=duration)
	animation.write_gif('matplotlib.gif', fps=20)


Working in the Jupyter Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are working inside a Jupyter Notebook, you can take advantage of the fact that VideoClips can be embedded in the output cells of the notebook with the `ipython_display` method. The above example then becomes: ::

	import matplotlib.pyplot as plt
	import numpy as np
	from moviepy.editor import VideoClip
	from moviepy.video.io.bindings import mplfig_to_npimage

	x = np.linspace(-2, 2, 200) 

	duration = 2

	fig, ax = plt.subplots()
	def make_frame(t):
	    ax.clear()
	    ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
	    ax.set_ylim(-1.5, 2.5)
	    return mplfig_to_npimage(fig)
	    
	animation = VideoClip(make_frame, duration=duration)
	animation.ipython_display(fps=20, loop=True, autoplay=True)