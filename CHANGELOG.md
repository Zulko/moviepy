# Changelog

All notable changes to this project will be documented in this file.

The format from v2.0.0 onwards is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/zulko/moviepy/tree/master)

[Full Changelog](https://github.com/zulko/moviepy/compare/v2.0.0.dev2...HEAD)

### Important Announcements

### Added <!-- for new features -->
- Support for `copy.copy(clip)` and `copy.deepcopy(clip)` with same behaviour as `clip.copy()` [\#1442](https://github.com/Zulko/moviepy/pull/1442)
- `audio.fx.multiply_stereo_volume` to control volume by audio channels [\#1424](https://github.com/Zulko/moviepy/pull/1424)
- Support for retrieve clip frames number using `clip.n_frames` [\#1471](https://github.com/Zulko/moviepy/pull/1471)
- `AudioClip.max_volume(stereo=True)` now can return more than 2 channels [\#1464](https://github.com/Zulko/moviepy/pull/1464)
- `video.io.ffmpeg_reader.ffmpeg_parse_infos` returns data from all streams by FFmpeg inputs in attribute `inputs` [\#1466](https://github.com/Zulko/moviepy/pull/1466)
- `video.io.ffmpeg_reader.ffmpeg_parse_infos` returns metadata of the container in attribute `metadata` [\#1466](https://github.com/Zulko/moviepy/pull/1466)
- `center`, `translate` and `bg_color` arguments to `video.fx.rotate` [\#1474](https://github.com/Zulko/moviepy/pull/1474)
- `audio.fx.audio_delay` FX [\#1481](https://github.com/Zulko/moviepy/pull/1481)
- `start_time` and `end_time` optional arguments to `multiply_volume` FX which allow to specify a range applying the transformation [\#1572](https://github.com/Zulko/moviepy/pull/1572)
- `loop` argument support writing GIFs with ffmpeg for `write_gif` and `write_gif_with_tempfiles` [\#1605](https://github.com/Zulko/moviepy/pull/1605)

### Changed <!-- for changes in existing functionality -->
- Lots of method and parameter names have been changed. This will be explained better in the documentation soon. See https://github.com/Zulko/moviepy/pull/1170 for more information. [\#1170](https://github.com/Zulko/moviepy/pull/1170)
- Changed recommended import from `import moviepy.editor` to `import moviepy`. This change is fully backwards compatible [\#1340](https://github.com/Zulko/moviepy/pull/1340)
- Renamed `audio.fx.volumex` to `audio.fx.multiply_volume` [\#1424](https://github.com/Zulko/moviepy/pull/1424)
- Renamed `cols_widths` argument of `clips_array` function by `cols_heights` [\#1465](https://github.com/Zulko/moviepy/pull/1465)
- `video_nframes` attribute of dictionary returned from `ffmpeg_parse_infos` renamed to `video_n_frames` [\#1471](https://github.com/Zulko/moviepy/pull/1471)
- Renamed `colorx` FX by `multiply_color` [\#1475](https://github.com/Zulko/moviepy/pull/1475)
- Renamed `speedx` FX by `multiply_speed` [\#1478](https://github.com/Zulko/moviepy/pull/1478)
- `make_loopable` transition must be used as FX [\#1477](https://github.com/Zulko/moviepy/pull/1477)
- `requests` package is no longer a dependency [\#1566](https://github.com/Zulko/moviepy/pull/1566)
- `accel_decel` FX raises `ValueError` if `sooness` parameter value is lower than zero [\#1546](https://github.com/Zulko/moviepy/pull/1546)
- `Clip.subclip` raise `ValueError` if `start_time >= clip.duration` (previously printing a message to stdout only if `start_time > clip.duration`) [\#1589](https://github.com/Zulko/moviepy/pull/1589)
- Allow to pass times in `HH:MM:SS` format to `t` argument of `clip.show` method [\#1594](https://github.com/Zulko/moviepy/pull/1594)
- `TextClip` now raises `ValueError` if none of the `text` or `filename` arguments are specified [\#1842](https://github.com/Zulko/moviepy/pull/1842)

### Deprecated <!-- for soon-to-be removed features -->
- `moviepy.video.fx.all` and `moviepy.audio.fx.all`. Use the fx method directly from the clip instance or import the fx function from `moviepy.video.fx` and `moviepy.audio.fx`. [\#1105](https://github.com/Zulko/moviepy/pull/1105)

### Removed <!-- for now removed features -->
- `VideoFileClip.coreader` and `AudioFileClip.coreader` methods removed. Use `VideoFileClip.copy` and `AudioFileClip.copy` instead [\#1442](https://github.com/Zulko/moviepy/pull/1442)
- `audio.fx.audio_loop` removed. Use `video.fx.loop` instead for all types of clip [\#1451](https://github.com/Zulko/moviepy/pull/1451)
- `video.compositing.on_color` removed. Use `VideoClip.on_color` instead [\#1456](https://github.com/Zulko/moviepy/pull/1456)

### Fixed <!-- for any bug fixes -->
- Fixed BitmapClip with fps != 1 not returning the correct frames or crashing [\#1333](https://github.com/Zulko/moviepy/pull/1333)
- Fixed `rotate` sometimes failing with `ValueError: axes don't match array` [\#1335](https://github.com/Zulko/moviepy/pull/1335)
- Fixed positioning error generating frames in `CompositeVideoClip` [\#1420](https://github.com/Zulko/moviepy/pull/1420)
- Changed deprecated `tostring` method by `tobytes` in `video.io.gif_writers::write_gif` [\#1429](https://github.com/Zulko/moviepy/pull/1429)
- Fixed calling `audio_normalize` on a clip with no sound causing `ZeroDivisionError` [\#1401](https://github.com/Zulko/moviepy/pull/1401)
- Fixed `freeze` FX was freezing at time minus 1 second as the end [\#1461](https://github.com/Zulko/moviepy/pull/1461)
- Fixed `Clip.cutout` transformation not being applied to audio [\#1468](https://github.com/Zulko/moviepy/pull/1468)
- Fixed arguments inconsistency in `video.tools.drawing.color_gradient` [\#1467](https://github.com/Zulko/moviepy/pull/1467)
- Fixed `fps` not defined in `CompositeAudioClip` at initialization [\#1462](https://github.com/Zulko/moviepy/pull/1462)
- Fixed `clip.preview()` crashing at exit when running inside Jupyter Notebook in Windows [\#1537](https://github.com/Zulko/moviepy/pull/1537)
- Fixed rotate FX not being applied to mask images [\#1399](https://github.com/Zulko/moviepy/pull/1399)
- Fixed opacity error blitting VideoClips [\#1552](https://github.com/Zulko/moviepy/pull/1552)
- Fixed rotation metadata of input not being taken into account rendering VideoClips [\#577](https://github.com/Zulko/moviepy/pull/577)
- Fixed mono clips crashing when `audio_fadein` FX applied [\#1574](https://github.com/Zulko/moviepy/pull/1574)
- Fixed mono clips crashing when `audio_fadeout` FX applied [\#1578](https://github.com/Zulko/moviepy/pull/1578)
- Fixed scroll FX not being scrolling [\#1591](https://github.com/Zulko/moviepy/pull/1591)
- Fixed parsing FFMPEG streams with square brackets [\#1781](https://github.com/Zulko/moviepy/pull/1781)
- Fixed audio processing for streams with missing `audio_bitrate` [\#1783](https://github.com/Zulko/moviepy/pull/1783)
- Fixed parsing language from stream output with square brackets [\#1837](https://github.com/Zulko/moviepy/pull/1837)


## [v2.0.0.dev2](https://github.com/zulko/moviepy/tree/v2.0.0.dev2) (2020-10-05)

[Full Changelog](https://github.com/zulko/moviepy/compare/v2.0.0.dev1...v2.0.0.dev2)

There are still no major breaking changes compared to v1.0.3. Expect them to come in the next dev update.
Any new changes made to the master branch will now be instantly reflected at https://moviepy.readthedocs.io, which is where documentation for all versions will be in the future. [\#1328](https://github.com/Zulko/moviepy/pull/1328)
Install with `pip install moviepy --pre --upgrade`.

### Added <!-- for new features -->
- New `pix_fmt` parameter in `VideoFileClip`, `VideoClip.write_videofile()`, `VideoClip.write_gif()` that allows passing a custom `pix_fmt` parameter such as `"bgr24"` to FFmpeg [\#1237](https://github.com/Zulko/moviepy/pull/1237)
- New `change_duration` parameter in `Clip.set_fps()` that allows changing the video speed to match the new fps [\#1329](https://github.com/Zulko/moviepy/pull/1329)

### Changed <!-- for changes in existing functionality -->
- `ffmpeg_parse_infos()` and `VideoFileClip` now have optional `decode_file` parameter that ensures that the detected duration is correct, but may take a long time to run [\#1063](https://github.com/Zulko/moviepy/pull/1063), [\#1222](https://github.com/Zulko/moviepy/pull/1222)
- `ffmpeg_parse_infos()` and `VideoFileClip` now use `fps` metadata instead of `tbr` to detect a video's fps value [\#1222](https://github.com/Zulko/moviepy/pull/1222)
- `FFMPEG_AudioReader.close_proc()` -> `FFMPEG_AudioReader.close()` for consistency with `FFMPEG_VideoReader` [\#1220](https://github.com/Zulko/moviepy/pull/1220)

### Fixed <!-- for any bug fixes -->
- Fixed `ffmpeg_tools.ffmpeg_extract_subclip` creating clips with incorrect duration metadata [\#1317](https://github.com/Zulko/moviepy/pull/1317)
- `OSError: MoviePy error: failed to read the first frame of video file...` would occasionally occur for no reason [\#1220](https://github.com/Zulko/moviepy/pull/1220)
- Fixed warnings being suppressed [\#1191](https://github.com/Zulko/moviepy/pull/1191)
- Fixed `UnicodeDecodeError` crash when file metadata contained non-UTF8 characters [\#959](https://github.com/Zulko/moviepy/pull/959)


## [v2.0.0.dev1](https://github.com/zulko/moviepy/tree/v2.0.0.dev1) (2020-06-04)

[Full Changelog](https://github.com/zulko/moviepy/compare/v1.0.3...v2.0.0.dev1)

This development version introduces many bug-fixes and changes. Please note that there may be large backwards-incompatible changes between dev versions! 
The online documentation has not been updated to reflect the changes in the v2.0.0 branch, so for help on how to use the new features please refer to the docstrings in the source code.
Install with `pip install moviepy --pre --upgrade`.

### Important Announcements
- Support removed for Python versions 2.7, 3.4 & 3.5 [\#1103](https://github.com/Zulko/moviepy/pull/1103), [\#1106](https://github.com/Zulko/moviepy/pull/1106)
- If you were previously setting custom locations for FFmpeg or ImageMagick in ``config_defaults.py`` and MoviePy still cannot autodetect the binaries, you will need to switch to the new method using enviroment variables. [\#1109](https://github.com/Zulko/moviepy/pull/1109)
- All previously deprecated methods and parameters have been removed [\#1115](https://github.com/Zulko/moviepy/pull/1115)

### Added <!-- for new features -->
- BitmapClip allows creating of custom frames using strings of letters
- Clips can now be tested for equality with other clips using `==`. This checks whether every frame of the two clips are identical
- Support for path-like objects as an option wherever filenames are passed in as arguments [\#1137](https://github.com/Zulko/moviepy/pull/1137)
- Autodetect ImageMagick executable on Windows [\#1109](https://github.com/Zulko/moviepy/pull/1109)
- Optionally configure paths to FFmpeg and ImageMagick binaries with environment variables or a ``.env`` file [\#1109](https://github.com/Zulko/moviepy/pull/1109)
- Optional `encoding` parameter in `SubtitlesClip` [\#1043](https://github.com/Zulko/moviepy/pull/1043)
- Added new `ffmpeg_stabilize_video()` function in `ffmpeg_tools`
- Optional `temp_audiofile_path` parameter in `VideoClip.write_videofile()` to specify where the temporary audiofile should be created [\#1144](https://github.com/Zulko/moviepy/pull/1144)
- `VideoClip.set_layer()` to specify the layer of the clip for use when creating a `CompositeVideoClip` [\#1176](https://github.com/Zulko/moviepy/pull/1176)
- `ffmpeg_parse_infos` additionally returns `"video_bitrate"` and `"audio_bitrate"` values [\#930](https://github.com/Zulko/moviepy/pull/930)
- Access to the source video's bitrate in a `VideoFileClip` or `AudioFileClip` through `videoclip.reader.bitrate` and `audioclip.reader.bitrate` [\#930](https://github.com/Zulko/moviepy/pull/930)

### Changed <!-- for changes in existing functionality -->
- `vfx.scroll` arguments `w` and `h` have had their order swapped. The correct order is now `w, h` but it is preferable to explicitly use keyword arguments
- Removed extra `.` in the output file name of `ffmpeg_extract_subclip()` when `targetname` is not specified [\#939](https://github.com/Zulko/moviepy/pull/939)

### Removed <!-- for now removed features -->
- Support removed for Python versions 2.7, 3.4 & 3.5
- Setting paths to ImageMagick and FFMpeg binaries in ``config_defaults.py`` is no longer possible [\#1109](https://github.com/Zulko/moviepy/pull/1109)
- Removed ``config.get_setting()`` and ``config.change_settings()`` functions [\#1109](https://github.com/Zulko/moviepy/pull/1109)
- All previously deprecated methods and parameters [\#1115](https://github.com/Zulko/moviepy/pull/1115):
    - `AudioClip.to_audiofile()` -> use `AudioClip.write_audiofile()`
    - `VideoClip.to_videofile()` -> use `VideoClip.write_videofile()`
    - `VideoClip.to_images_sequence()` -> use `VideoClip.write_images_sequence()`
    - `concatenate()` -> use `concatenate_videoclips()`
    - `verbose` parameter in `AudioClip.write_audiofile()`, `ffmpeg_audiowriter()`, `VideoFileClip()`, `VideoClip.write_videofile()`, `VideoClip.write_images_sequence()`, `ffmpeg_write_video()`, `write_gif()`, `write_gif_with_tempfiles()`, `write_gif_with_image_io()` -> Instead of `verbose=False`, use `logger=None`
    - `verbose_print()` -> no replacement
    - `col` parameter in `ColorClip()` -> use `color`

### Fixed <!-- for any bug fixes -->
- When using `VideoClip.write_videofile()` with `write_logfile=True`, errors would not be properly reported [\#890](https://github.com/Zulko/moviepy/pull/890)
- `TextClip.list("color")` now returns a list of bytes, not strings [\#1119](https://github.com/Zulko/moviepy/pull/1119)
- `TextClip.search("colorname", "color")` does not crash with a TypeError [\#1119](https://github.com/Zulko/moviepy/pull/1119)
- `vfx.even_size` previously created clips with odd sizes [\#1124](https://github.com/Zulko/moviepy/pull/1124)
- `IndexError` in `vfx.freeze`, `vfx.time_mirror` and `vfx.time_symmetrize` [\#1124](https://github.com/Zulko/moviepy/pull/1124)
- Using `rotate()` with a `ColorClip` no longer crashes [\#1139](https://github.com/Zulko/moviepy/pull/1139)
- `AudioFileClip` would not generate audio identical to the original file [\#1108](https://github.com/Zulko/moviepy/pull/1108)
- Fixed `TypeError` when using `filename` instead of `txt` parameter in `TextClip` [\#1201](https://github.com/Zulko/moviepy/pull/1201)
- Several issues resulting from incorrect time values due to floating point errors [\#1195](https://github.com/Zulko/moviepy/pull/1195), for example:
    - Blank frames at the end of clips [\#210](https://github.com/Zulko/moviepy/pull/210)
    - Sometimes getting `IndexError: list index out of range` when using `concatenate_videoclips` [\#646](https://github.com/Zulko/moviepy/pull/646)
- Applying `resize` with a non-constant `newsize` to a clip with a mask would remove the mask [\#1200](https://github.com/Zulko/moviepy/pull/1200)
- Using `color_gradient()` would crash with `ValueError: The truth value of an array with more than one element is ambiguous` [\#1212](https://github.com/Zulko/moviepy/pull/1212)


## [v1.0.3](https://github.com/zulko/moviepy/tree/v1.0.3) (2020-05-07)

[Full Changelog](https://github.com/zulko/moviepy/compare/v1.0.2...v1.0.3)

Bonus release to fix critical error when working with audio: `AttributeError: 'NoneType' object has no attribute 'stdout'` [\#1185](https://github.com/Zulko/moviepy/pull/1185)


## [v1.0.2](https://github.com/zulko/moviepy/tree/v1.0.2) (2020-03-26)

[Full Changelog](https://github.com/zulko/moviepy/compare/v1.0.1...v1.0.2)

Note that this is likely to be the last release before v2.0, which will drop support for Python versions 2.7, 3.4 & 3.5 and will introduce other backwards-incompatible changes.

**Notable bug fixes:**

- Fixed bug that meant that some VideoFileClips were created without audio [\#968](https://github.com/Zulko/moviepy/pull/968)
- Fixed bug so now the `slide_out` effect works [\#795](https://github.com/Zulko/moviepy/pull/795)


**Fixed bugs:**

- Fixed potential crash trying to call the logger string as a function [\#1082](https://github.com/Zulko/moviepy/pull/1082) ([tburrows13](https://github.com/tburrows13))
- Get ffmpeg to use all audio streams [\#1008](https://github.com/Zulko/moviepy/pull/1008) ([vmaliaev](https://github.com/vmaliaev))
- Reorder FFMPEG\_VideoWriter command arguments [\#968](https://github.com/Zulko/moviepy/pull/968) ([ThePhonon](https://github.com/ThePhonon))
- Test that the temporary audio file exists [\#958](https://github.com/Zulko/moviepy/pull/958) ([ybenitezf](https://github.com/ybenitezf))
- Fix slide out [\#795](https://github.com/Zulko/moviepy/pull/795) ([knezi](https://github.com/knezi))
- Correct the error message to new filename. [\#1057](https://github.com/Zulko/moviepy/pull/1057) ([jwg4](https://github.com/jwg4))

**Merged pull requests:**

- Remove timer in stdout flushing test [\#1091](https://github.com/Zulko/moviepy/pull/1091) ([tburrows13](https://github.com/tburrows13))
- Update github issue and PR templates [\#1087](https://github.com/Zulko/moviepy/pull/1087) ([tburrows13](https://github.com/tburrows13))
- Clean up imports [\#1084](https://github.com/Zulko/moviepy/pull/1084) ([tburrows13](https://github.com/tburrows13))
- refactor Pythonic sake [\#1077](https://github.com/Zulko/moviepy/pull/1077) ([mgaitan](https://github.com/mgaitan))
- Upgrade pip by calling via python \(in appveyor\). [\#1067](https://github.com/Zulko/moviepy/pull/1067) ([jwg4](https://github.com/jwg4))
- Improve afx.audio\_normalize documentation [\#1046](https://github.com/Zulko/moviepy/pull/1046) ([dspinellis](https://github.com/dspinellis))
- Add Travis support for Python 3.7 and 3.8 [\#1018](https://github.com/Zulko/moviepy/pull/1018) ([tburrows13](https://github.com/tburrows13))
- Hide pygame support prompt [\#1017](https://github.com/Zulko/moviepy/pull/1017) ([tburrows13](https://github.com/tburrows13))

**Closed issues:**

- ImageSequenceClip   write\_videofile [\#1098](https://github.com/Zulko/moviepy/issues/1098)
- Formatting code with Black [\#1097](https://github.com/Zulko/moviepy/issues/1097)
- Make effects be callable classes [\#1096](https://github.com/Zulko/moviepy/issues/1096)
- URGENT - Documentation is inaccessible [\#1086](https://github.com/Zulko/moviepy/issues/1086)
- Drop support for python \< 3.6 [\#1081](https://github.com/Zulko/moviepy/issues/1081)
- TextClip filenotfounderror winerror2 [\#1080](https://github.com/Zulko/moviepy/issues/1080)
- unable to create video from images [\#1074](https://github.com/Zulko/moviepy/issues/1074)
- Crash on loading the video, windows 10 [\#1071](https://github.com/Zulko/moviepy/issues/1071)
- Audio Issue while concatenate\_videoclips'ing ImageClip and VideoFileClip \(contains audio already\) [\#1064](https://github.com/Zulko/moviepy/issues/1064)
- AttributeError: 'NoneType' object has no attribute 'stdout' [\#1054](https://github.com/Zulko/moviepy/issues/1054)
- Overlay a video on top of an image with Moviepy [\#1053](https://github.com/Zulko/moviepy/issues/1053)
- get\_frame fails if not an early frame [\#1052](https://github.com/Zulko/moviepy/issues/1052)
- from google.colab import drive drive.mount\('/content/drive'\)  import cv2 import numpy as np from skimage import morphology from IPython import display import PIL  image = cv2.imread\('/content/drive/My Drive/CAR3/11.JPG',cv2.IMREAD\_COLOR\)  from google.colab.patches import cv2\_imshow  \#image = cv2.resize\(image,\(384,192\)\)  cv2\_imshow\(image\) [\#1051](https://github.com/Zulko/moviepy/issues/1051)
- Segmentation fault \(core dumped\) [\#1048](https://github.com/Zulko/moviepy/issues/1048)
- zip over two iter\_frames functions doesn't render proper result [\#1047](https://github.com/Zulko/moviepy/issues/1047)
- CompositeVideoClip\(\[xxx\]\).rotate\(90\)  ValueError: axes don't match array [\#1042](https://github.com/Zulko/moviepy/issues/1042)
- to\_soundarray Index error [\#1034](https://github.com/Zulko/moviepy/issues/1034)
- write\_videofile does not add audio [\#1032](https://github.com/Zulko/moviepy/issues/1032)
- moviepy.video.io.VideoFileClip.VideoFileClip.set\_audio does not set audio [\#1030](https://github.com/Zulko/moviepy/issues/1030)
- loop for concatenate\_videoclips [\#1027](https://github.com/Zulko/moviepy/issues/1027)
- How to resize ImageClip? [\#1004](https://github.com/Zulko/moviepy/issues/1004)
- Pygame pollutes stdio with spammy message [\#985](https://github.com/Zulko/moviepy/issues/985)
- Issue with ffmpeg version [\#934](https://github.com/Zulko/moviepy/issues/934)
- No release notes for 1.0.0? [\#917](https://github.com/Zulko/moviepy/issues/917)
- Imageio's new use of imageio-ffmpeg [\#908](https://github.com/Zulko/moviepy/issues/908)
- `ModuleNotFound: No module named 'imageio\_ffmpeg'`, or imageio v2.5.0 is breaking ffmpeg detection in config [\#906](https://github.com/Zulko/moviepy/issues/906)
- CompositeVideoClip has no audio [\#876](https://github.com/Zulko/moviepy/issues/876)
- Handling of the ffmpeg dependency [\#859](https://github.com/Zulko/moviepy/issues/859)
- 'ffmpeg-linux64-v3.3.1' was not found on your computer; downloading it now. [\#839](https://github.com/Zulko/moviepy/issues/839)
- Typo in variable name in transitions.py\(t\_s instead of ts\) [\#692](https://github.com/Zulko/moviepy/issues/692)
- version 0.2.3.2 TypeError: must be str, not bytes [\#650](https://github.com/Zulko/moviepy/issues/650)
- AWS Lambda - Moviepy Error -  [\#638](https://github.com/Zulko/moviepy/issues/638)
- Adding conda-forge package [\#616](https://github.com/Zulko/moviepy/issues/616)
- Several YouTube examples in Gallery page are unable to load. [\#600](https://github.com/Zulko/moviepy/issues/600)
- ffmpeg not installed on Mac [\#595](https://github.com/Zulko/moviepy/issues/595)
- FFMPEG not downloaded [\#493](https://github.com/Zulko/moviepy/issues/493)
- Fix documentation [\#482](https://github.com/Zulko/moviepy/issues/482)
- Moviepy is producing garbled videos [\#356](https://github.com/Zulko/moviepy/issues/356)
- Help with contributing to the documentation? [\#327](https://github.com/Zulko/moviepy/issues/327)
- audio custom filter documentation? [\#267](https://github.com/Zulko/moviepy/issues/267)
- Mistake in doc,  clips.html part. [\#136](https://github.com/Zulko/moviepy/issues/136)


## [v1.0.1](https://github.com/zulko/moviepy/tree/v1.0.1) (2019-10-01)

[Full Changelog](https://github.com/zulko/moviepy/compare/v1.0.0...v1.0.1)

**Implemented enhancements:**

- Thoughts on re-routing tqdm progress bar for external use? [\#412](https://github.com/Zulko/moviepy/issues/412)
- Progress bar [\#128](https://github.com/Zulko/moviepy/issues/128)

**Fixed bugs:**

- More resilient Windows CI regarding fetching ImageMagick binaries [\#941](https://github.com/Zulko/moviepy/pull/941) ([Overdrivr](https://github.com/Overdrivr))
- \[docker\] drop the not needed download and symlink of ffmpeg [\#916](https://github.com/Zulko/moviepy/pull/916) ([das7pad](https://github.com/das7pad))

**Closed issues:**

- website video examples broken videos [\#1019](https://github.com/Zulko/moviepy/issues/1019)
- Audio glitches when using concatenate\_videoclips. [\#1005](https://github.com/Zulko/moviepy/issues/1005)
- txt\_clip = TextClip\(filename='learn.srt'\) --bug:TypeError: stat: path should be string, bytes, os.PathLike or integer, not NoneType [\#984](https://github.com/Zulko/moviepy/issues/984)
- txt\_clip = TextClip\(filename='learn.srt'\) --bug:TypeError: stat: path should be string, bytes, os.PathLike or integer, not NoneType [\#983](https://github.com/Zulko/moviepy/issues/983)
- txt\_clip = TextClip\(filename='learn.srt'\)path should be string, bytes, os.PathLike or integer, not NoneType [\#982](https://github.com/Zulko/moviepy/issues/982)
- write\_videofile writes blank black when writing grayscale [\#973](https://github.com/Zulko/moviepy/issues/973)
- i dont understand this question [\#967](https://github.com/Zulko/moviepy/issues/967)
- Thank you guys! [\#957](https://github.com/Zulko/moviepy/issues/957)
- Saving an opencv stream [\#953](https://github.com/Zulko/moviepy/issues/953)
- Issue with reader not being defined [\#950](https://github.com/Zulko/moviepy/issues/950)
- On Windows, ImageMagick needs to be installed with Utility mode for the convert.exe file to exist [\#937](https://github.com/Zulko/moviepy/issues/937)
- extract subtitles [\#932](https://github.com/Zulko/moviepy/issues/932)
- ffmpeg\_parse\_infos silently hangs on Windows when MP4 file contains enough metadata [\#926](https://github.com/Zulko/moviepy/issues/926)
- crop missing from moviepy.video.fx.all [\#914](https://github.com/Zulko/moviepy/issues/914)
- Segmentation Error on VPS [\#912](https://github.com/Zulko/moviepy/issues/912)
- Error when installing with imageio [\#911](https://github.com/Zulko/moviepy/issues/911)
- Backwards compatibility [\#889](https://github.com/Zulko/moviepy/issues/889)
- frozen seconds in beginning of subclip using ffmpeg\_extract\_subclip\(\) [\#847](https://github.com/Zulko/moviepy/issues/847)
- \[Errno 3\] No such process : on Windows Sub Linux \(ubuntu 16.x\) [\#765](https://github.com/Zulko/moviepy/issues/765)
- Progress bar newline error in Jupyter [\#740](https://github.com/Zulko/moviepy/issues/740)
- Refer to magick on https://zulko.github.io/moviepy/install.html [\#689](https://github.com/Zulko/moviepy/issues/689)
- Configure Appveyor support [\#628](https://github.com/Zulko/moviepy/issues/628)
- tqdm progress bar write\_videofile send to iterator [\#568](https://github.com/Zulko/moviepy/issues/568)
- ffmpeg\_extract\_subclip returns black frames [\#508](https://github.com/Zulko/moviepy/issues/508)
- Windows: specifying path to ImageMagick in config\_defaults.py [\#378](https://github.com/Zulko/moviepy/issues/378)
- AttributeError: 'NoneType' object has no attribute 'start' [\#191](https://github.com/Zulko/moviepy/issues/191)
- ImageMagick write gif success but no file found  [\#113](https://github.com/Zulko/moviepy/issues/113)

**Merged pull requests:**

- Create v1.0.1 [\#1023](https://github.com/Zulko/moviepy/pull/1023) ([tburrows13](https://github.com/tburrows13))
- Update maintainer list in the README [\#1022](https://github.com/Zulko/moviepy/pull/1022) ([tburrows13](https://github.com/tburrows13))
- fixed small error in 'Clip' documentation [\#1002](https://github.com/Zulko/moviepy/pull/1002) ([thomasmatt88](https://github.com/thomasmatt88))
- Specify Coverage version explicitly. [\#987](https://github.com/Zulko/moviepy/pull/987) ([Julian-O](https://github.com/Julian-O))
- Updating Docs for ImageMagick Installing Guide [\#980](https://github.com/Zulko/moviepy/pull/980) ([ABODFTW](https://github.com/ABODFTW))
- Several ImageMagick related bug fixes [\#972](https://github.com/Zulko/moviepy/pull/972) ([KiLLAAA](https://github.com/KiLLAAA))
- Auto-detect image magick latest 6.9.X-Y version [\#936](https://github.com/Zulko/moviepy/pull/936) ([Overdrivr](https://github.com/Overdrivr))
- Windows-based testing [\#931](https://github.com/Zulko/moviepy/pull/931) ([Overdrivr](https://github.com/Overdrivr))
- Fix formatting in logger [\#929](https://github.com/Zulko/moviepy/pull/929) ([tnoff](https://github.com/tnoff))
- Fix for \#926 [\#927](https://github.com/Zulko/moviepy/pull/927) ([Overdrivr](https://github.com/Overdrivr))
- Invalid video URL in docs/getting\_started/compositing [\#921](https://github.com/Zulko/moviepy/pull/921) ([gepcel](https://github.com/gepcel))
- Do not install tests in site-packages [\#880](https://github.com/Zulko/moviepy/pull/880) ([cgohlke](https://github.com/cgohlke))
- FIX changed order of specifications -ss befor -i for ffmpeg\_extract\_subclip\(\) [\#848](https://github.com/Zulko/moviepy/pull/848) ([grszkthfr](https://github.com/grszkthfr))

## [v1.0.0](https://github.com/zulko/moviepy/tree/v1.0.0) (2019-02-17)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.3.5...v1.0.0)

**Closed issues:**

- Can't overlay gizeh animation onto video with transparency/mask [\#898](https://github.com/Zulko/moviepy/issues/898)
- \[0.2.4.0\] Garbled audio when exporting mp3 from mp4? [\#891](https://github.com/Zulko/moviepy/issues/891)
- Error with VideoFileClip\(filePath\) [\#868](https://github.com/Zulko/moviepy/issues/868)
- I am trying to run this code [\#867](https://github.com/Zulko/moviepy/issues/867)
- Out of memory exception [\#862](https://github.com/Zulko/moviepy/issues/862)
- simple problem on the first step: importing moviepy.editor [\#852](https://github.com/Zulko/moviepy/issues/852)
- MoviePy insert multiple images in a video [\#840](https://github.com/Zulko/moviepy/issues/840)
- Videogrep can't works with Moviepy in Windows [\#834](https://github.com/Zulko/moviepy/issues/834)
- File "\<stdin\>", line 1 error [\#832](https://github.com/Zulko/moviepy/issues/832)
- ImageMagick error - Ubuntu 16.04  [\#831](https://github.com/Zulko/moviepy/issues/831)
- Combining thousands of small clips into one file [\#827](https://github.com/Zulko/moviepy/issues/827)
- TypeError: 'ImageClip' object is not iterable [\#824](https://github.com/Zulko/moviepy/issues/824)
- OSError: \[WinError 6\] The handle is invalid... concatenating clips [\#823](https://github.com/Zulko/moviepy/issues/823)
- How to add audio tracks. not to replace it. [\#822](https://github.com/Zulko/moviepy/issues/822)
- Missing 'ffmpeg-win32-v3.2.4.exe' [\#821](https://github.com/Zulko/moviepy/issues/821)
- No sound with an audio clip add to an video in quicktime [\#820](https://github.com/Zulko/moviepy/issues/820)
- Pip fails when trying to install [\#812](https://github.com/Zulko/moviepy/issues/812)
- PermissionError after trying to delete a file after it's purpose is done [\#810](https://github.com/Zulko/moviepy/issues/810)
- video clip from URI [\#780](https://github.com/Zulko/moviepy/issues/780)
- Fails on FreeBSD [\#756](https://github.com/Zulko/moviepy/issues/756)
- inconsistent behaviour of clip.get\_frame\(\) [\#751](https://github.com/Zulko/moviepy/issues/751)
- Error with write\_videofile [\#727](https://github.com/Zulko/moviepy/issues/727)
- Trying to use moviepy on lambda, but has problem with ffmpeg [\#642](https://github.com/Zulko/moviepy/issues/642)
- Unexpected Behavior With negative t\_start in Subclip [\#341](https://github.com/Zulko/moviepy/issues/341)
- Could not find a format to read the specified file in mode 'i'  [\#219](https://github.com/Zulko/moviepy/issues/219)
- WindowsError\[5\] and AttributeError Exception [\#170](https://github.com/Zulko/moviepy/issues/170)
- Can't make VideoFileClip 'utf8' [\#169](https://github.com/Zulko/moviepy/issues/169)
- Rendered output missing first frame [\#155](https://github.com/Zulko/moviepy/issues/155)
- Incorrect output when concatenate\_videoclips two quicktime videos [\#144](https://github.com/Zulko/moviepy/issues/144)
- a bytes object is recognised as a string [\#120](https://github.com/Zulko/moviepy/issues/120)

**Merged pull requests:**

- New version of imageio with imageio\_ffmpeg for python 3.4+ [\#907](https://github.com/Zulko/moviepy/pull/907) ([Zulko](https://github.com/Zulko))
- fix typo that introduces audio regression [\#894](https://github.com/Zulko/moviepy/pull/894) ([chrox](https://github.com/chrox))
- modified max duration error for better understanding [\#875](https://github.com/Zulko/moviepy/pull/875) ([kapilkd13](https://github.com/kapilkd13))
- Fixed typo in docstring for VideoClip class [\#871](https://github.com/Zulko/moviepy/pull/871) ([Armcollector](https://github.com/Armcollector))
- Fix a small typing error [\#845](https://github.com/Zulko/moviepy/pull/845) ([yuvallanger](https://github.com/yuvallanger))

## [v0.2.3.5](https://github.com/zulko/moviepy/tree/v0.2.3.5) (2018-05-31)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.3.4...v0.2.3.5)

**Fixed bugs:**

- Removed Hz from audio\_fps match in ffmpeg\_parse\_infos [\#665](https://github.com/Zulko/moviepy/pull/665) ([qmac](https://github.com/qmac))

**Closed issues:**

- 100% of GIF does not convert to MP4, gets cut short. [\#802](https://github.com/Zulko/moviepy/issues/802)
- How to add audio track to MP4? [\#794](https://github.com/Zulko/moviepy/issues/794)
- ffmpeg 4.0 NVIDIA NVDEC-accelerated Support ? [\#790](https://github.com/Zulko/moviepy/issues/790)
- Help!!!! errors during installation on Mac [\#788](https://github.com/Zulko/moviepy/issues/788)
- Blink fx uses deprecated\(?\) method `with\_mask\(\)` [\#786](https://github.com/Zulko/moviepy/issues/786)
- Built-in file downloader downloads files repeatedly? [\#779](https://github.com/Zulko/moviepy/issues/779)
- Error in compositing video and SubtitlesClip by CompositeVideoClip  [\#778](https://github.com/Zulko/moviepy/issues/778)
- SubtitlesClip [\#777](https://github.com/Zulko/moviepy/issues/777)
- Video Background [\#774](https://github.com/Zulko/moviepy/issues/774)

**Merged pull requests:**

- fixing the git remote syntax in documentions [\#887](https://github.com/Zulko/moviepy/pull/887) ([ishandutta2007](https://github.com/ishandutta2007))
- Progress bar optional for GIF creation [\#799](https://github.com/Zulko/moviepy/pull/799) ([mdfirman](https://github.com/mdfirman))
- Added contributing guide and issue template [\#792](https://github.com/Zulko/moviepy/pull/792) ([tburrows13](https://github.com/tburrows13))

## [v0.2.3.4](https://github.com/zulko/moviepy/tree/v0.2.3.4) (2018-04-22)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.3.3...v0.2.3.4)

**Closed issues:**

- fail to install [\#771](https://github.com/Zulko/moviepy/issues/771)
- install moviepy [\#758](https://github.com/Zulko/moviepy/issues/758)
- How to prepend hexadecimal data to a binary file? [\#757](https://github.com/Zulko/moviepy/issues/757)
- It’s time for a new release [\#742](https://github.com/Zulko/moviepy/issues/742)
- wrong video duration value when concatenating videos with method = compose [\#574](https://github.com/Zulko/moviepy/issues/574)

**Merged pull requests:**

- Added `fullscreen` parameter to `preview\(\)` [\#773](https://github.com/Zulko/moviepy/pull/773) ([tburrows13](https://github.com/tburrows13))
- add pcm\_s24le codec [\#769](https://github.com/Zulko/moviepy/pull/769) ([lsde](https://github.com/lsde))

## [v0.2.3.3](https://github.com/zulko/moviepy/tree/v0.2.3.3) (2018-04-17)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.3.2...v0.2.3.3)

**Implemented enhancements:**

- Use feature detection instead of version detection [\#721](https://github.com/Zulko/moviepy/pull/721) ([cclauss](https://github.com/cclauss))
- Fixed Optional Progress Bar in cuts/detect\_scenes [\#587](https://github.com/Zulko/moviepy/pull/587) ([scherroman](https://github.com/scherroman))
- Fix travis build and enable pip caching [\#561](https://github.com/Zulko/moviepy/pull/561) ([mbeacom](https://github.com/mbeacom))
- Avoid mutable default arguments [\#553](https://github.com/Zulko/moviepy/pull/553) ([mbeacom](https://github.com/mbeacom))
- add ImageSequenceClip image size exception  [\#550](https://github.com/Zulko/moviepy/pull/550) ([earney](https://github.com/earney))

**Fixed bugs:**

- Added ffmpeg download when importing moviepy.editor [\#731](https://github.com/Zulko/moviepy/pull/731) ([tburrows13](https://github.com/tburrows13))
- Fixed bugs, neater code, changed docstrings in audiofiles [\#722](https://github.com/Zulko/moviepy/pull/722) ([tburrows13](https://github.com/tburrows13))
- Resolve undefined name execfile in Python 3 [\#718](https://github.com/Zulko/moviepy/pull/718) ([cclauss](https://github.com/cclauss))
- Fix credits, added tests [\#716](https://github.com/Zulko/moviepy/pull/716) ([tburrows13](https://github.com/tburrows13))
- res —\> size to align with line 62 [\#710](https://github.com/Zulko/moviepy/pull/710) ([cclauss](https://github.com/cclauss))
- Add gap=0 to align with lines 40, 97, and 98 [\#709](https://github.com/Zulko/moviepy/pull/709) ([cclauss](https://github.com/cclauss))
- import numpy as np for lines 151 and 178 [\#708](https://github.com/Zulko/moviepy/pull/708) ([cclauss](https://github.com/cclauss))
- Convert advanced\_tools.py to valid Python [\#707](https://github.com/Zulko/moviepy/pull/707) ([cclauss](https://github.com/cclauss))
- Added missing '%' operator for string formatting. [\#686](https://github.com/Zulko/moviepy/pull/686) ([taylorjdawson](https://github.com/taylorjdawson))
- Addressing \#655 [\#656](https://github.com/Zulko/moviepy/pull/656) ([gyglim](https://github.com/gyglim))
- initialize proc to None [\#637](https://github.com/Zulko/moviepy/pull/637) ([gyglim](https://github.com/gyglim))
- sometimes tempfile.tempdir is None, so use tempfile.gettempdir\(\) function instead [\#633](https://github.com/Zulko/moviepy/pull/633) ([earney](https://github.com/earney))
- Issue629 [\#630](https://github.com/Zulko/moviepy/pull/630) ([Julian-O](https://github.com/Julian-O))
- Fixed bug in Clip.set\_duration\(\) [\#613](https://github.com/Zulko/moviepy/pull/613) ([kencochrane](https://github.com/kencochrane))
- Fixed typo in the slide\_out transition [\#612](https://github.com/Zulko/moviepy/pull/612) ([kencochrane](https://github.com/kencochrane))
- Exceptions do not have a .message attribute. [\#603](https://github.com/Zulko/moviepy/pull/603) ([Julian-O](https://github.com/Julian-O))
- Issue \#574, fix duration of masks when using concatenate\(.., method="compose"\) [\#585](https://github.com/Zulko/moviepy/pull/585) ([earney](https://github.com/earney))
- Fix out of bounds error [\#570](https://github.com/Zulko/moviepy/pull/570) ([shawwn](https://github.com/shawwn))
- fixed ffmpeg error reporting on Python 3 [\#565](https://github.com/Zulko/moviepy/pull/565) ([narfdotpl](https://github.com/narfdotpl))
- Add int\(\) wrapper to scroll to prevent floats [\#528](https://github.com/Zulko/moviepy/pull/528) ([tburrows13](https://github.com/tburrows13))
- Fix issue \#464, repeated/skipped frames in ImageSequenceClip [\#494](https://github.com/Zulko/moviepy/pull/494) ([neitzal](https://github.com/neitzal))
- fixes \#248 issue with VideoFileClip\(\) not reading all frames [\#251](https://github.com/Zulko/moviepy/pull/251) ([aldilaff](https://github.com/aldilaff))

**Closed issues:**

- Overly Restrictive Requirements [\#767](https://github.com/Zulko/moviepy/issues/767)
- Using a gif as an ImageClip? [\#764](https://github.com/Zulko/moviepy/issues/764)
- How can I include a moving 'arrow' in a clip? [\#762](https://github.com/Zulko/moviepy/issues/762)
- How to call moviepy.video.fx.all.crop\(\) ? [\#760](https://github.com/Zulko/moviepy/issues/760)
- ImportError: Imageio Pillow requires Pillow, not PIL!  [\#748](https://github.com/Zulko/moviepy/issues/748)
- Fail to call VideoFileClip\(\) because of WinError 6 [\#746](https://github.com/Zulko/moviepy/issues/746)
- concatenate\_videoclips with fadein fadeout [\#743](https://github.com/Zulko/moviepy/issues/743)
- Ignore - sorry! [\#739](https://github.com/Zulko/moviepy/issues/739)
- Image becomes blurr with high fps [\#735](https://github.com/Zulko/moviepy/issues/735)
- Https protocol not found with ffmpeg [\#732](https://github.com/Zulko/moviepy/issues/732)
- Storing Processed Video clip takes a long time [\#726](https://github.com/Zulko/moviepy/issues/726)
- image corruption when concatenating images of different sizes [\#725](https://github.com/Zulko/moviepy/issues/725)
- How to install MoviePy on OS High Sierra [\#706](https://github.com/Zulko/moviepy/issues/706)
- Issue when running the first example of text overlay in ubuntu 16.04 with python3 [\#703](https://github.com/Zulko/moviepy/issues/703)
- Extracting frames [\#702](https://github.com/Zulko/moviepy/issues/702)
- Error - The handle is invalid - Windows Only [\#697](https://github.com/Zulko/moviepy/issues/697)
- ImageMagick not detected by moviepy while using SubtitlesClip [\#693](https://github.com/Zulko/moviepy/issues/693)
- Textclip is not working at all [\#691](https://github.com/Zulko/moviepy/issues/691)
- Remove Python 3.3 testing ? [\#688](https://github.com/Zulko/moviepy/issues/688)
- In idle, 25 % CPU [\#676](https://github.com/Zulko/moviepy/issues/676)
- Audio error [\#675](https://github.com/Zulko/moviepy/issues/675)
- Insert a ImageClip in a CompositeVideoClip. How to add nil audio [\#669](https://github.com/Zulko/moviepy/issues/669)
- Issue with nesting context managers [\#655](https://github.com/Zulko/moviepy/issues/655)
- Output video is garbled, single frames output are fine [\#651](https://github.com/Zulko/moviepy/issues/651)
- 'missing handle' error [\#644](https://github.com/Zulko/moviepy/issues/644)
- issue with proc being None [\#636](https://github.com/Zulko/moviepy/issues/636)
- Looping parameter is missing from write\_gif\_with\_image\_io\(\) [\#629](https://github.com/Zulko/moviepy/issues/629)
- would it be optionally possible to use pgmagick package ? \(instead of ImageMagick binary\) [\#625](https://github.com/Zulko/moviepy/issues/625)
- concatenate\_videoclips\(\) can't handle TextClips [\#622](https://github.com/Zulko/moviepy/issues/622)
- Writing movie one frame at a time [\#619](https://github.com/Zulko/moviepy/issues/619)
- Fatal Python error: PyImport\_GetModuleDict: no module dictionary! [\#618](https://github.com/Zulko/moviepy/issues/618)
- line 54, in requires\_duration return [\#601](https://github.com/Zulko/moviepy/issues/601)
- test\_duration\(\) fails in test\_TextClip\(\) [\#598](https://github.com/Zulko/moviepy/issues/598)
- Geting framesize from moviepy [\#571](https://github.com/Zulko/moviepy/issues/571)
- Write\_videofile results in 1930x1080 even when I force clip.resize\(width=1920,height=1080\) before write\_videofile [\#547](https://github.com/Zulko/moviepy/issues/547)
- Is there one potential bug in FFMPEG\_READER? [\#546](https://github.com/Zulko/moviepy/issues/546)
- vfx.scroll giving TypeError: slice indices must be integers or None or have an \_\_index\_\_ method [\#527](https://github.com/Zulko/moviepy/issues/527)
- AttributeError: AudioFileClip instance has no attribute 'afx' [\#513](https://github.com/Zulko/moviepy/issues/513)
- ImageSequenceClip repeats frames depending on fps [\#464](https://github.com/Zulko/moviepy/issues/464)
- manual\_tracking format issue [\#373](https://github.com/Zulko/moviepy/issues/373)
- resize video when time changed trigger a error [\#334](https://github.com/Zulko/moviepy/issues/334)
- WindowsError: \[Error 5\] Access is denied [\#294](https://github.com/Zulko/moviepy/issues/294)
- TypeError in Adding Soundtrack [\#279](https://github.com/Zulko/moviepy/issues/279)
- IndexError when converting audio to\_soundarray\(\) [\#246](https://github.com/Zulko/moviepy/issues/246)
- Defaults fail for ImageSequenceClip\(\) [\#218](https://github.com/Zulko/moviepy/issues/218)
- Unable to use unicode strings with Python 2 [\#76](https://github.com/Zulko/moviepy/issues/76)
- audio normalization [\#32](https://github.com/Zulko/moviepy/issues/32)
- Unclosed processes. [\#19](https://github.com/Zulko/moviepy/issues/19)

**Merged pull requests:**

- transitions.py: pep8 and a change to docstring [\#754](https://github.com/Zulko/moviepy/pull/754) ([tburrows13](https://github.com/tburrows13))
- Make TextClip work on Travis CI [\#747](https://github.com/Zulko/moviepy/pull/747) ([tburrows13](https://github.com/tburrows13))
- Added tests, new duration arg in to\_ImageClip\(\) [\#724](https://github.com/Zulko/moviepy/pull/724) ([tburrows13](https://github.com/tburrows13))
- let there be \(more\) colour [\#723](https://github.com/Zulko/moviepy/pull/723) ([bashu](https://github.com/bashu))
- Resolve undefined name unicode in Python 3 [\#717](https://github.com/Zulko/moviepy/pull/717) ([cclauss](https://github.com/cclauss))
- Credits.py PEP 8 [\#715](https://github.com/Zulko/moviepy/pull/715) ([tburrows13](https://github.com/tburrows13))
- Added info about tag wiki [\#714](https://github.com/Zulko/moviepy/pull/714) ([tburrows13](https://github.com/tburrows13))
- Remove testing support for Python 3.3, closes \#688 [\#713](https://github.com/Zulko/moviepy/pull/713) ([tburrows13](https://github.com/tburrows13))
- More PEP8 compliance [\#712](https://github.com/Zulko/moviepy/pull/712) ([tburrows13](https://github.com/tburrows13))
- More PEP8 compliance [\#711](https://github.com/Zulko/moviepy/pull/711) ([tburrows13](https://github.com/tburrows13))
- flake8 test to find syntax errors, undefined names [\#705](https://github.com/Zulko/moviepy/pull/705) ([cclauss](https://github.com/cclauss))
- fix typo [\#687](https://github.com/Zulko/moviepy/pull/687) ([msrks](https://github.com/msrks))
- Update Readme.rst [\#671](https://github.com/Zulko/moviepy/pull/671) ([rlphillips](https://github.com/rlphillips))
- Update Dockerfile to add requests module [\#664](https://github.com/Zulko/moviepy/pull/664) ([edouard-mangel](https://github.com/edouard-mangel))
- fixed typo in library include [\#652](https://github.com/Zulko/moviepy/pull/652) ([Goddard](https://github.com/Goddard))
- Use max fps for CompositeVideoClip [\#610](https://github.com/Zulko/moviepy/pull/610) ([scherroman](https://github.com/scherroman))
- Add audio normalization function [\#609](https://github.com/Zulko/moviepy/pull/609) ([dspinellis](https://github.com/dspinellis))
- \#600: Several YouTube examples in Gallery page won't load. [\#606](https://github.com/Zulko/moviepy/pull/606) ([Julian-O](https://github.com/Julian-O))
- Two small corrections to documentation. [\#605](https://github.com/Zulko/moviepy/pull/605) ([Julian-O](https://github.com/Julian-O))
- PEP 8 compatible [\#582](https://github.com/Zulko/moviepy/pull/582) ([gpantelis](https://github.com/gpantelis))
- add additional ImageSequenceClip test [\#551](https://github.com/Zulko/moviepy/pull/551) ([earney](https://github.com/earney))
- General tests cleanup [\#549](https://github.com/Zulko/moviepy/pull/549) ([mbeacom](https://github.com/mbeacom))
- Update docs [\#548](https://github.com/Zulko/moviepy/pull/548) ([tburrows13](https://github.com/tburrows13))
- add tests for most fx functions [\#545](https://github.com/Zulko/moviepy/pull/545) ([earney](https://github.com/earney))

## [v0.2.3.2](https://github.com/zulko/moviepy/tree/v0.2.3.2) (2017-04-13)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.3.1...v0.2.3.2)

**Implemented enhancements:**

- Requirements adjustments [\#530](https://github.com/Zulko/moviepy/issues/530)
- Modify setup.py handling [\#531](https://github.com/Zulko/moviepy/pull/531) ([mbeacom](https://github.com/mbeacom))
- Resolve documentation build errors [\#526](https://github.com/Zulko/moviepy/pull/526) ([mbeacom](https://github.com/mbeacom))

**Closed issues:**

- Youtube videos fail to load in documentation [\#536](https://github.com/Zulko/moviepy/issues/536)
- unicodeDecoderError by running the setup.py during moviepy pip install [\#532](https://github.com/Zulko/moviepy/issues/532)
- Documentation build failures [\#525](https://github.com/Zulko/moviepy/issues/525)
- Index is out of bounds - AudioFileClip [\#521](https://github.com/Zulko/moviepy/issues/521)
- Should we push another version? [\#481](https://github.com/Zulko/moviepy/issues/481)
- Add matplotlib example to the user guide? [\#421](https://github.com/Zulko/moviepy/issues/421)
- Fails to list fx after freezing an app with moviepy [\#274](https://github.com/Zulko/moviepy/issues/274)
- Documentation doesn't match ffmpeg presets [\#232](https://github.com/Zulko/moviepy/issues/232)

**Merged pull requests:**

- add opencv dependency since headblur effect depends on it. [\#540](https://github.com/Zulko/moviepy/pull/540) ([earney](https://github.com/earney))
- create tests for blackwhite, colorx, fadein, fadeout [\#539](https://github.com/Zulko/moviepy/pull/539) ([earney](https://github.com/earney))
- add crop tests [\#538](https://github.com/Zulko/moviepy/pull/538) ([earney](https://github.com/earney))
- Fix youtube video rendering in documentation [\#537](https://github.com/Zulko/moviepy/pull/537) ([mbeacom](https://github.com/mbeacom))
- Update docs [\#535](https://github.com/Zulko/moviepy/pull/535) ([tburrows13](https://github.com/tburrows13))
- add test for Issue 334, PR 336 [\#534](https://github.com/Zulko/moviepy/pull/534) ([earney](https://github.com/earney))
- issue-212: add rotation info from metadata [\#529](https://github.com/Zulko/moviepy/pull/529) ([taddyhuo](https://github.com/taddyhuo))
- Added another project using MoviePy [\#509](https://github.com/Zulko/moviepy/pull/509) ([justswim](https://github.com/justswim))
- added doc for working with matplotlib [\#465](https://github.com/Zulko/moviepy/pull/465) ([flothesof](https://github.com/flothesof))
- fix issue \#334 [\#336](https://github.com/Zulko/moviepy/pull/336) ([bluedazzle](https://github.com/bluedazzle))
- Add progress\_bar option to write\_images\_sequence [\#300](https://github.com/Zulko/moviepy/pull/300) ([achalddave](https://github.com/achalddave))
- write\_videofile preset choices doc [\#282](https://github.com/Zulko/moviepy/pull/282) ([gcandal](https://github.com/gcandal))

## [v0.2.3.1](https://github.com/zulko/moviepy/tree/v0.2.3.1) (2017-04-05)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.2.13...v0.2.3.1)

**Implemented enhancements:**

- \[Windows users: help !\] Finding ImageMagick automatically on windows [\#80](https://github.com/Zulko/moviepy/issues/80)
- Save to Amazon S3 [\#6](https://github.com/Zulko/moviepy/issues/6)
- Fix for cleaning up os calls through Popen [\#501](https://github.com/Zulko/moviepy/pull/501) ([gyglim](https://github.com/gyglim))
- pick highest fps when concatenating [\#416](https://github.com/Zulko/moviepy/pull/416) ([BrianLee608](https://github.com/BrianLee608))

**Closed issues:**

- concatenate\_videoclips\(\[clip1,clip2\]\) results in a clip where the second clip is skewed and has severe lines [\#520](https://github.com/Zulko/moviepy/issues/520)
- FFMPEG crashes if the script is a .pyw [\#517](https://github.com/Zulko/moviepy/issues/517)
- VideoFileClip instance has no attribute 'reader' [\#512](https://github.com/Zulko/moviepy/issues/512)
- Adding emoji with moviepy [\#507](https://github.com/Zulko/moviepy/issues/507)
- How to remove original audio from the video file ? [\#504](https://github.com/Zulko/moviepy/issues/504)
- Duration Format With Moviepy [\#502](https://github.com/Zulko/moviepy/issues/502)
- AttributeError: 'numpy.ndarray' object has no attribute 'tobytes' [\#499](https://github.com/Zulko/moviepy/issues/499)
- Possible to create out of bounds subclip [\#470](https://github.com/Zulko/moviepy/issues/470)
- New install... VideoFileClip\("x.mp4"\).subclip\(0,13\) gives "reader not defined error" [\#461](https://github.com/Zulko/moviepy/issues/461)
- Bytes-like object is required, not 'str' in version 0.2.2.13 [\#455](https://github.com/Zulko/moviepy/issues/455)
- Can't import gifs into moviepy [\#452](https://github.com/Zulko/moviepy/issues/452)
-  AudioFileClip [\#448](https://github.com/Zulko/moviepy/issues/448)
- Error with Pillow [\#445](https://github.com/Zulko/moviepy/issues/445)
- Moviepy AttributeError: 'NoneType' object has no attribute 'shape' [\#439](https://github.com/Zulko/moviepy/issues/439)
- This is what exception.... [\#437](https://github.com/Zulko/moviepy/issues/437)
- when I from moviepy.editor import \*,  There cause exception,That's why....... [\#436](https://github.com/Zulko/moviepy/issues/436)
- No available fonts in moviepy [\#426](https://github.com/Zulko/moviepy/issues/426)
- Project maintenance, mgmt, workflow etc. [\#422](https://github.com/Zulko/moviepy/issues/422)
- Cannot run in a django project on apache [\#420](https://github.com/Zulko/moviepy/issues/420)
- error 'unicode' object has no attribute 'shape' [\#417](https://github.com/Zulko/moviepy/issues/417)
- VideoClip has no attribute fps error when trying to concatenate [\#407](https://github.com/Zulko/moviepy/issues/407)
- The Travis tester seems to be failing [\#406](https://github.com/Zulko/moviepy/issues/406)
- Slow motion video massively sped up [\#404](https://github.com/Zulko/moviepy/issues/404)
- moviepy not able to find installed ffmpeg    bug? [\#396](https://github.com/Zulko/moviepy/issues/396)
- Cannot open audio: AttributeError: 'NoneType' object has no attribute 'start' [\#393](https://github.com/Zulko/moviepy/issues/393)
- DirectoryClip??? Where is it? [\#385](https://github.com/Zulko/moviepy/issues/385)
- TypeError: 'float' object cannot be interpreted as an integer [\#376](https://github.com/Zulko/moviepy/issues/376)
- Minor Documentation typo in VideoFileClip [\#375](https://github.com/Zulko/moviepy/issues/375)
- Documentation Update: VideoTools [\#372](https://github.com/Zulko/moviepy/issues/372)
- TextClip.list\('color'\) failed to return color list [\#371](https://github.com/Zulko/moviepy/issues/371)
- ValueError: Invalid value for quantizer: 'wu' [\#368](https://github.com/Zulko/moviepy/issues/368)
- Parameter color in ColorClip [\#366](https://github.com/Zulko/moviepy/issues/366)
- Different size videos [\#365](https://github.com/Zulko/moviepy/issues/365)
- Bug in write\_gif [\#359](https://github.com/Zulko/moviepy/issues/359)
- Add support for dithering GIF output [\#358](https://github.com/Zulko/moviepy/issues/358)
- VideoFileClip instance has no attribute 'coreader' [\#357](https://github.com/Zulko/moviepy/issues/357)
- crossfadeout "Attribute 'duration' not set" [\#354](https://github.com/Zulko/moviepy/issues/354)
- ffmpeg\_parse\_infos fails while parsing tbr [\#352](https://github.com/Zulko/moviepy/issues/352)
- No audio when adding Mp3 to VideoFileClip MoviePy [\#350](https://github.com/Zulko/moviepy/issues/350)
- ImportError: No module named tracking \(OS: 10.11.6 "El Capitan", Python 2.7.12\) [\#348](https://github.com/Zulko/moviepy/issues/348)
- AAC support for mp4 [\#344](https://github.com/Zulko/moviepy/issues/344)
- Moviepy not compatible with Python 3.2 [\#333](https://github.com/Zulko/moviepy/issues/333)
- Attribute Error \(Raspberry Pi\) [\#332](https://github.com/Zulko/moviepy/issues/332)
- ImageSequenceClip: Error when fps not provided but durations provided [\#326](https://github.com/Zulko/moviepy/issues/326)
- CI Testing [\#325](https://github.com/Zulko/moviepy/issues/325)
- Pythonanywhere Moviepy [\#324](https://github.com/Zulko/moviepy/issues/324)
- Documentation for resize parameter is wrong [\#319](https://github.com/Zulko/moviepy/issues/319)
- ImageClip's with default settings can not be concatenated [\#314](https://github.com/Zulko/moviepy/issues/314)
- librelist does not work [\#309](https://github.com/Zulko/moviepy/issues/309)
- Broken Gallery in Documentation [\#304](https://github.com/Zulko/moviepy/issues/304)
- File IOError when trying to extract subclips from mov file on Ubuntu [\#303](https://github.com/Zulko/moviepy/issues/303)
- write\_gif failing [\#296](https://github.com/Zulko/moviepy/issues/296)
- Python2 unicode\_literals errors [\#293](https://github.com/Zulko/moviepy/issues/293)
- concatenate ImageClip  [\#285](https://github.com/Zulko/moviepy/issues/285)
- Resize not working [\#272](https://github.com/Zulko/moviepy/issues/272)
- VideoFileClip instance has no attribute 'reader' [\#255](https://github.com/Zulko/moviepy/issues/255)
- stretch image to size of frame [\#250](https://github.com/Zulko/moviepy/issues/250)
- ffprobe metadata on video file clips [\#249](https://github.com/Zulko/moviepy/issues/249)
- Credits1 is not working - gap missing, isTransparent flag not available [\#247](https://github.com/Zulko/moviepy/issues/247)
- Generating Gif from images [\#240](https://github.com/Zulko/moviepy/issues/240)
- permission denied [\#233](https://github.com/Zulko/moviepy/issues/233)
- receive the video advancement mounting \(Ex: in %\) [\#224](https://github.com/Zulko/moviepy/issues/224)
- Import of MoviePy and Mayavi causes a segfault [\#223](https://github.com/Zulko/moviepy/issues/223)
- Video overlay \(gauges...\) [\#222](https://github.com/Zulko/moviepy/issues/222)
- OSError: \[WinError 193\] %1 n’est pas une application Win32 valide [\#221](https://github.com/Zulko/moviepy/issues/221)
- Warning: skimage.filter is deprecated [\#214](https://github.com/Zulko/moviepy/issues/214)
- TextClip.list\('color'\) fails [\#200](https://github.com/Zulko/moviepy/issues/200)
- External FFmpeg issues [\#193](https://github.com/Zulko/moviepy/issues/193)
- Video and Audio are out of sync after write [\#192](https://github.com/Zulko/moviepy/issues/192)
- Broken image on PyPI [\#187](https://github.com/Zulko/moviepy/issues/187)
- ImageSequenceClip from OpenEXR file sequence generate black Clip video [\#186](https://github.com/Zulko/moviepy/issues/186)
- Loading video from url [\#185](https://github.com/Zulko/moviepy/issues/185)
- Wrong number of frames in .gif file [\#181](https://github.com/Zulko/moviepy/issues/181)
- Converting mp4 to ogv error in bitrate [\#174](https://github.com/Zulko/moviepy/issues/174)
- embed clip in a jupyter notebook [\#160](https://github.com/Zulko/moviepy/issues/160)
- How to create a video from a sequence of images without writing them on memory [\#159](https://github.com/Zulko/moviepy/issues/159)
- LaTeX strings [\#156](https://github.com/Zulko/moviepy/issues/156)
- UnboundLocalError in video/compositing/concatenate.py [\#145](https://github.com/Zulko/moviepy/issues/145)
- Crop a Video with four different coodinate pairs [\#142](https://github.com/Zulko/moviepy/issues/142)
- global name 'colorGradient' is not defined [\#141](https://github.com/Zulko/moviepy/issues/141)
- rotating image animation producing error [\#130](https://github.com/Zulko/moviepy/issues/130)
- bug introduced in 0.2.2.11? [\#129](https://github.com/Zulko/moviepy/issues/129)
- Getting a TypeError in FramesMatch [\#126](https://github.com/Zulko/moviepy/issues/126)
- moviepy is awesome [\#125](https://github.com/Zulko/moviepy/issues/125)
- Concanate clips with different size [\#124](https://github.com/Zulko/moviepy/issues/124)
- TextClip.list\('font'\) raises TypeError in Python 3 [\#117](https://github.com/Zulko/moviepy/issues/117)
- Attempt to Download freeimage failing [\#111](https://github.com/Zulko/moviepy/issues/111)
- Invalid buffer size, packet size \< expected frame\_size [\#109](https://github.com/Zulko/moviepy/issues/109)
- imageio has permission problems as WSGI user on Amazon Web Server [\#106](https://github.com/Zulko/moviepy/issues/106)
- transparency bug in concatenate\_videoclips\(\) [\#103](https://github.com/Zulko/moviepy/issues/103)
- Possibility to avoid code duplication [\#99](https://github.com/Zulko/moviepy/issues/99)
- Memory Leak In VideoFileClip [\#96](https://github.com/Zulko/moviepy/issues/96)

**Merged pull requests:**

- create test for Trajectory.save\_list/load\_list [\#523](https://github.com/Zulko/moviepy/pull/523) ([earney](https://github.com/earney))
- add Dockerfile [\#522](https://github.com/Zulko/moviepy/pull/522) ([earney](https://github.com/earney))
- Add fps\_source option for \#404 [\#516](https://github.com/Zulko/moviepy/pull/516) ([tburrows13](https://github.com/tburrows13))
- Minor Modifications [\#515](https://github.com/Zulko/moviepy/pull/515) ([gpantelis](https://github.com/gpantelis))
- \#485 followup [\#514](https://github.com/Zulko/moviepy/pull/514) ([tburrows13](https://github.com/tburrows13))
- Correcting text [\#510](https://github.com/Zulko/moviepy/pull/510) ([gpantelis](https://github.com/gpantelis))
- Add aspect\_ratio @property to VideoClip [\#503](https://github.com/Zulko/moviepy/pull/503) ([scherroman](https://github.com/scherroman))
- add test for ffmpeg\_parse\_info [\#498](https://github.com/Zulko/moviepy/pull/498) ([earney](https://github.com/earney))
- add scipy for py2.7 on travis-ci [\#497](https://github.com/Zulko/moviepy/pull/497) ([earney](https://github.com/earney))
- add file\_to\_subtitles test [\#496](https://github.com/Zulko/moviepy/pull/496) ([earney](https://github.com/earney))
- add a subtitle test [\#495](https://github.com/Zulko/moviepy/pull/495) ([earney](https://github.com/earney))
- add afterimage example [\#491](https://github.com/Zulko/moviepy/pull/491) ([earney](https://github.com/earney))
- add doc example to tests [\#490](https://github.com/Zulko/moviepy/pull/490) ([earney](https://github.com/earney))
- Allow resizing frames in ffmpeg when reading [\#489](https://github.com/Zulko/moviepy/pull/489) ([gyglim](https://github.com/gyglim))
- Fix class name in AudioClip doc strings [\#488](https://github.com/Zulko/moviepy/pull/488) ([withpower](https://github.com/withpower))
- convert POpen stderr.read to communicate [\#487](https://github.com/Zulko/moviepy/pull/487) ([earney](https://github.com/earney))
- add tests for find\_video\_period [\#486](https://github.com/Zulko/moviepy/pull/486) ([earney](https://github.com/earney))
- refer to MoviePy as library \(was: module\) [\#484](https://github.com/Zulko/moviepy/pull/484) ([keikoro](https://github.com/keikoro))
- include requirements file for docs [\#483](https://github.com/Zulko/moviepy/pull/483) ([keikoro](https://github.com/keikoro))
- add test for issue 354; duration not set [\#478](https://github.com/Zulko/moviepy/pull/478) ([earney](https://github.com/earney))
- Issue 470, reading past audio file EOF [\#476](https://github.com/Zulko/moviepy/pull/476) ([earney](https://github.com/earney))
- Issue 285,  error adding durations \(int and None\). [\#472](https://github.com/Zulko/moviepy/pull/472) ([earney](https://github.com/earney))
- Issue 359,  fix default opt argument to work with imageio and ImageMagick [\#471](https://github.com/Zulko/moviepy/pull/471) ([earney](https://github.com/earney))
- Add tests for TextClip [\#469](https://github.com/Zulko/moviepy/pull/469) ([earney](https://github.com/earney))
- Issue 467;  fix  Nameerror with copy function.  Added issue to tests.. [\#468](https://github.com/Zulko/moviepy/pull/468) ([earney](https://github.com/earney))
- Small improvements to docs pages, docs usage [\#463](https://github.com/Zulko/moviepy/pull/463) ([keikoro](https://github.com/keikoro))
- Fix mixed content [\#462](https://github.com/Zulko/moviepy/pull/462) ([keikoro](https://github.com/keikoro))
- fix Issue 368..  ValueError: Invalid value for quantizer: 'wu' [\#460](https://github.com/Zulko/moviepy/pull/460) ([earney](https://github.com/earney))
- add testing to verify the width,height \(size\) are correct. [\#459](https://github.com/Zulko/moviepy/pull/459) ([earney](https://github.com/earney))
- Adds `progress\_bar` option to `write\_audiofile\(\)` to complement \#380  [\#458](https://github.com/Zulko/moviepy/pull/458) ([tburrows13](https://github.com/tburrows13))
- modify tests to use ColorClip's new color argument \(instead of col\) [\#457](https://github.com/Zulko/moviepy/pull/457) ([earney](https://github.com/earney))
- add ImageSequenceClip tests [\#456](https://github.com/Zulko/moviepy/pull/456) ([earney](https://github.com/earney))
- Add some tests for VideoFileClip [\#453](https://github.com/Zulko/moviepy/pull/453) ([earney](https://github.com/earney))
- add test\_compositing.py [\#451](https://github.com/Zulko/moviepy/pull/451) ([earney](https://github.com/earney))
- add test for tools [\#450](https://github.com/Zulko/moviepy/pull/450) ([earney](https://github.com/earney))
- fix issue 448; AudioFileClip 90k tbr error [\#449](https://github.com/Zulko/moviepy/pull/449) ([earney](https://github.com/earney))
- add testing with travis-ci [\#447](https://github.com/Zulko/moviepy/pull/447) ([earney](https://github.com/earney))
- fix YouTube embeds in docs [\#446](https://github.com/Zulko/moviepy/pull/446) ([keikoro](https://github.com/keikoro))
- Move PR test to test\_PR.py file [\#444](https://github.com/Zulko/moviepy/pull/444) ([earney](https://github.com/earney))
- Test issue 407 \(video has a valid fps after concatenate function\) [\#443](https://github.com/Zulko/moviepy/pull/443) ([earney](https://github.com/earney))
- add test for PR306. [\#440](https://github.com/Zulko/moviepy/pull/440) ([earney](https://github.com/earney))
- fix issue 417..  unicode has no attribute shape  \(error in python 2\) [\#438](https://github.com/Zulko/moviepy/pull/438) ([earney](https://github.com/earney))
- fix Issue \#385 ,  no DirectoryClip class [\#434](https://github.com/Zulko/moviepy/pull/434) ([earney](https://github.com/earney))
- add test file for pull requests. [\#433](https://github.com/Zulko/moviepy/pull/433) ([earney](https://github.com/earney))
- put DEVNULL into compat.py [\#432](https://github.com/Zulko/moviepy/pull/432) ([earney](https://github.com/earney))
- test for issue \#145 [\#431](https://github.com/Zulko/moviepy/pull/431) ([earney](https://github.com/earney))
- fix PR \#413 . \(issue \#357\) [\#429](https://github.com/Zulko/moviepy/pull/429) ([earney](https://github.com/earney))
- fix issue 145.  raise Exception when concatenate method != chain or c… [\#428](https://github.com/Zulko/moviepy/pull/428) ([earney](https://github.com/earney))
- Readme improvements [\#425](https://github.com/Zulko/moviepy/pull/425) ([keikoro](https://github.com/keikoro))
- `Colorclip` changed `col`\>`color` [\#424](https://github.com/Zulko/moviepy/pull/424) ([tburrows13](https://github.com/tburrows13))
- Revert "small recipe \(mirroring a video\)" [\#414](https://github.com/Zulko/moviepy/pull/414) ([Zulko](https://github.com/Zulko))
- fixes \#357.  confusing error about coreader, when media file does not exist [\#413](https://github.com/Zulko/moviepy/pull/413) ([earney](https://github.com/earney))
- move PY3 to new compat.py file [\#411](https://github.com/Zulko/moviepy/pull/411) ([earney](https://github.com/earney))
- Fix Issue \#373 Trajectory.save\_list [\#394](https://github.com/Zulko/moviepy/pull/394) ([dermusikman](https://github.com/dermusikman))
- bug presented [\#390](https://github.com/Zulko/moviepy/pull/390) ([TonyChen0724](https://github.com/TonyChen0724))
- Incorporated optional progress\_bar flag for writing video to file [\#380](https://github.com/Zulko/moviepy/pull/380) ([wingillis](https://github.com/wingillis))
- Audio error handling made failsafe [\#377](https://github.com/Zulko/moviepy/pull/377) ([gyglim](https://github.com/gyglim))
- Fix issue \#354 [\#355](https://github.com/Zulko/moviepy/pull/355) ([groundflyer](https://github.com/groundflyer))
- Fixed resize documentation issue \#319 [\#346](https://github.com/Zulko/moviepy/pull/346) ([jmisacube](https://github.com/jmisacube))
- Added AAC codec to mp4 [\#345](https://github.com/Zulko/moviepy/pull/345) ([jeromegrosse](https://github.com/jeromegrosse))
- Add a test case. [\#339](https://github.com/Zulko/moviepy/pull/339) ([drewm1980](https://github.com/drewm1980))
- ImageSequenceClip: Check for fps and durations rather than fps and du… [\#331](https://github.com/Zulko/moviepy/pull/331) ([jeromegrosse](https://github.com/jeromegrosse))
- Handle bytes when listing fonts in VideoClip.py [\#306](https://github.com/Zulko/moviepy/pull/306) ([Zowie](https://github.com/Zowie))
- fix deprecation message [\#302](https://github.com/Zulko/moviepy/pull/302) ([mgaitan](https://github.com/mgaitan))
- Fix for \#274  [\#275](https://github.com/Zulko/moviepy/pull/275) ([nad2000](https://github.com/nad2000))
- Update README.rst [\#254](https://github.com/Zulko/moviepy/pull/254) ([tcyrus](https://github.com/tcyrus))
- small recipe \(mirroring a video\) [\#243](https://github.com/Zulko/moviepy/pull/243) ([zodman](https://github.com/zodman))
- Document inherited members in reference documentation [\#236](https://github.com/Zulko/moviepy/pull/236) ([achalddave](https://github.com/achalddave))
- fixed module hierarchy for Trajectory [\#215](https://github.com/Zulko/moviepy/pull/215) ([bwagner](https://github.com/bwagner))
- Fixed missing list [\#211](https://github.com/Zulko/moviepy/pull/211) ([LunarLanding](https://github.com/LunarLanding))
- Fixed copy-paste typo [\#197](https://github.com/Zulko/moviepy/pull/197) ([temerick](https://github.com/temerick))

## [v0.2.2.13](https://github.com/zulko/moviepy/tree/v0.2.2.13) (2017-02-15)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.2.12...v0.2.2.13)

**Implemented enhancements:**

- Add `self.filename` as a `VideoFileClip` attribute [\#405](https://github.com/Zulko/moviepy/pull/405) ([tburrows13](https://github.com/tburrows13))

**Closed issues:**

- keep github releases in sync with PyPI [\#398](https://github.com/Zulko/moviepy/issues/398)
- accidentally opened, sorry [\#397](https://github.com/Zulko/moviepy/issues/397)
- BrokenPipeError [\#349](https://github.com/Zulko/moviepy/issues/349)
- Bug in ffmpeg\_audiowriter.py for python 3 [\#335](https://github.com/Zulko/moviepy/issues/335)
- concatenate.py - Python3 incompatible [\#313](https://github.com/Zulko/moviepy/issues/313)

**Merged pull requests:**

- fix issue \#313, make concatenate\_videoclips python 3 compatible. [\#410](https://github.com/Zulko/moviepy/pull/410) ([earney](https://github.com/earney))
- Update maintainer section in README [\#409](https://github.com/Zulko/moviepy/pull/409) ([mbeacom](https://github.com/mbeacom))
- fix issue \#401 [\#403](https://github.com/Zulko/moviepy/pull/403) ([earney](https://github.com/earney))
- ensures int arguments to np.reshape; closes \#383 [\#384](https://github.com/Zulko/moviepy/pull/384) ([tyarkoni](https://github.com/tyarkoni))
- on\_color function docstring has wrong parameter [\#244](https://github.com/Zulko/moviepy/pull/244) ([cblument](https://github.com/cblument))

## [v0.2.2.12](https://github.com/zulko/moviepy/tree/v0.2.2.12) (2017-01-30)

[Full Changelog](https://github.com/zulko/moviepy/compare/v0.2.2...v0.2.2.12)

**Implemented enhancements:**

- Update version and readme to include maintainers section [\#395](https://github.com/Zulko/moviepy/pull/395) ([mbeacom](https://github.com/mbeacom))

**Closed issues:**

- Numpy 1.12.0 Breaks VideoFileClip [\#392](https://github.com/Zulko/moviepy/issues/392)
- read\_chunk\(\) breaks in numpy 1.12.0 [\#383](https://github.com/Zulko/moviepy/issues/383)
- Intel MKL FATAL ERROR: Cannot load libmkl\_avx.so or libmkl\_def.so [\#379](https://github.com/Zulko/moviepy/issues/379)
- Memory Error [\#370](https://github.com/Zulko/moviepy/issues/370)
- module 'cv2' has no attribute 'resize' [\#369](https://github.com/Zulko/moviepy/issues/369)
- Unable to load a gif created by moviepy. Fault of avconv? [\#337](https://github.com/Zulko/moviepy/issues/337)
- write\_videofile Error [\#330](https://github.com/Zulko/moviepy/issues/330)
- Does Moviepy work with a Raspberry Pi? [\#322](https://github.com/Zulko/moviepy/issues/322)
- moviepy.video.fx.all fadein and fadeout does not fade to any other color than black? [\#321](https://github.com/Zulko/moviepy/issues/321)
- Imageio: 'ffmpeg.osx' was not found on your computer; downloading it now. [\#320](https://github.com/Zulko/moviepy/issues/320)
- is there a way to composite a video with a alpha channel? [\#317](https://github.com/Zulko/moviepy/issues/317)
- ffmpeg never dies [\#312](https://github.com/Zulko/moviepy/issues/312)
- Mask Getting Called Multiple Times [\#299](https://github.com/Zulko/moviepy/issues/299)
- write\_videofile gets stuck [\#284](https://github.com/Zulko/moviepy/issues/284)
- zero-size array to reduction operation minimum which has no identity [\#269](https://github.com/Zulko/moviepy/issues/269)
- nvenc encoder nvidia [\#264](https://github.com/Zulko/moviepy/issues/264)
- Avoid writing to disk with ImageSequenceClip [\#261](https://github.com/Zulko/moviepy/issues/261)
- MemoryError [\#259](https://github.com/Zulko/moviepy/issues/259)
- Create multiple subclips using times from CSV file [\#257](https://github.com/Zulko/moviepy/issues/257)
- write\_videofile results in "No such file or directory: OSError" on AWS Lambda instance [\#256](https://github.com/Zulko/moviepy/issues/256)
- Pillow 3.0.0 drops support for `tostring\(\)` in favour of `tobytes\(\)` [\#241](https://github.com/Zulko/moviepy/issues/241)
- Add Environment Variable to overwrite FFMPEG\_BINARY [\#237](https://github.com/Zulko/moviepy/issues/237)
- Clip::subclip vs ffmpeg\_extract\_subclip? [\#235](https://github.com/Zulko/moviepy/issues/235)
- Moviepy - win2k8 64 install errors [\#234](https://github.com/Zulko/moviepy/issues/234)
- How to install MoviePy on a remote SSH server without an A/V card? [\#230](https://github.com/Zulko/moviepy/issues/230)
- Failed to read duration of file, Samsung S6 MP4s [\#226](https://github.com/Zulko/moviepy/issues/226)
- MoviePy error: FFMPEG permission error [\#220](https://github.com/Zulko/moviepy/issues/220)
- White artifacts around the image when rotating an ImageClip with a mask or just a png with transparency in angles that are not 0, 90, 180, 270 \( Added Examples to reproduce it \) [\#216](https://github.com/Zulko/moviepy/issues/216)
- Error when using ffmpeg\_movie\_from\_frames "global name 'bitrate' is not defined" [\#208](https://github.com/Zulko/moviepy/issues/208)
- Is it possible to write infinite looping videos? [\#206](https://github.com/Zulko/moviepy/issues/206)
- Problem creating VideoFileClip from URL on server [\#204](https://github.com/Zulko/moviepy/issues/204)
- Animate TextClip text value [\#199](https://github.com/Zulko/moviepy/issues/199)
- ffmpeg not available under Ubuntu 14.04 [\#189](https://github.com/Zulko/moviepy/issues/189)
- Zoom effect trembling [\#183](https://github.com/Zulko/moviepy/issues/183)
- How to match the speed of a gif after converting to a video [\#173](https://github.com/Zulko/moviepy/issues/173)
- \[Feature Request\] Zoom and Rotate [\#166](https://github.com/Zulko/moviepy/issues/166)
- Speed optimisation using multiple processes [\#163](https://github.com/Zulko/moviepy/issues/163)
- Invalid Syntax Error [\#161](https://github.com/Zulko/moviepy/issues/161)
- AudioFileClip bombs on file read [\#158](https://github.com/Zulko/moviepy/issues/158)
- Hamac example gives subprocess error [\#152](https://github.com/Zulko/moviepy/issues/152)
- unable to overwrite audio [\#151](https://github.com/Zulko/moviepy/issues/151)
- Error in /video/fx/freeze\_region.py [\#146](https://github.com/Zulko/moviepy/issues/146)
- Convert gif to video has back background at the end of the video [\#143](https://github.com/Zulko/moviepy/issues/143)
- How to conditionally chain effects? [\#138](https://github.com/Zulko/moviepy/issues/138)
- \[Feature Request\] Write output using newlines [\#137](https://github.com/Zulko/moviepy/issues/137)
- 。 [\#135](https://github.com/Zulko/moviepy/issues/135)
- How can add my logo to right top of entire mp4 video using moviepy ? [\#127](https://github.com/Zulko/moviepy/issues/127)
- numpy error on trying to concatenate [\#123](https://github.com/Zulko/moviepy/issues/123)
- NameError: global name 'clip' is not defined [\#114](https://github.com/Zulko/moviepy/issues/114)
- typo in line 626, in on\_color. elf is good for christmas, bad for function [\#107](https://github.com/Zulko/moviepy/issues/107)
- API request: clip.rotate [\#105](https://github.com/Zulko/moviepy/issues/105)
- Use graphicsmagick where available [\#90](https://github.com/Zulko/moviepy/issues/90)
- Packaging ffmpeg binary with moviepy [\#85](https://github.com/Zulko/moviepy/issues/85)
- Running VideoFileClip multiple times in django gives me error [\#73](https://github.com/Zulko/moviepy/issues/73)
- FFMPEG binary not found. [\#60](https://github.com/Zulko/moviepy/issues/60)

**Merged pull requests:**

- Fix \#164 - Resolve ffmpeg zombie processes [\#374](https://github.com/Zulko/moviepy/pull/374) ([mbeacom](https://github.com/mbeacom))
- Updated resize function to use cv2.INTER\_LINEAR when upsizing images … [\#268](https://github.com/Zulko/moviepy/pull/268) ([kuchi](https://github.com/kuchi))
- Read FFMPEG\_BINARY and/or IMAGEMAGICK\_BINARY environment variables [\#238](https://github.com/Zulko/moviepy/pull/238) ([dkarchmer](https://github.com/dkarchmer))
- Fixing a minor typo. [\#205](https://github.com/Zulko/moviepy/pull/205) ([TheNathanBlack](https://github.com/TheNathanBlack))
- Fixed minor typos in the docs [\#196](https://github.com/Zulko/moviepy/pull/196) ([bertyhell](https://github.com/bertyhell))
- added check for resolution before processing video stream [\#188](https://github.com/Zulko/moviepy/pull/188) ([ryanfox](https://github.com/ryanfox))
- Support for SRT files with any kind of newline [\#171](https://github.com/Zulko/moviepy/pull/171) ([factorial](https://github.com/factorial))
- Delete duplicated import os [\#168](https://github.com/Zulko/moviepy/pull/168) ([jsseb](https://github.com/jsseb))
- set correct lastindex variable in mask\_make\_frame [\#165](https://github.com/Zulko/moviepy/pull/165) ([Dennovin](https://github.com/Dennovin))
- fix to work with python3 [\#162](https://github.com/Zulko/moviepy/pull/162) ([laurentperrinet](https://github.com/laurentperrinet))
- poor error message from ffmpeg\_reader.py [\#157](https://github.com/Zulko/moviepy/pull/157) ([ryanfox](https://github.com/ryanfox))
- fixing region parameter on freeze\_region [\#147](https://github.com/Zulko/moviepy/pull/147) ([savannahniles](https://github.com/savannahniles))
- Typo [\#133](https://github.com/Zulko/moviepy/pull/133) ([rishabhjain](https://github.com/rishabhjain))
- setup.py: Link to website and state license [\#132](https://github.com/Zulko/moviepy/pull/132) ([techtonik](https://github.com/techtonik))
- Issue \#126 Fix FramesMatch repr and str. [\#131](https://github.com/Zulko/moviepy/pull/131) ([filipochnik](https://github.com/filipochnik))
- auto detection of ImageMagick binary on Windows [\#118](https://github.com/Zulko/moviepy/pull/118) ([carlodri](https://github.com/carlodri))
- Minor grammatical and spelling changes [\#115](https://github.com/Zulko/moviepy/pull/115) ([grimley517](https://github.com/grimley517))
- typo fix [\#108](https://github.com/Zulko/moviepy/pull/108) ([stonebig](https://github.com/stonebig))
- additional safe check in close\_proc [\#100](https://github.com/Zulko/moviepy/pull/100) ([Eloar](https://github.com/Eloar))
- Allows user to pass additional parameters to ffmpeg when writing audio clips [\#94](https://github.com/Zulko/moviepy/pull/94) ([jdelman](https://github.com/jdelman))

## [v0.2.2](https://github.com/zulko/moviepy/tree/v0.2.2) (2014-12-11)

[Full Changelog](https://github.com/zulko/moviepy/compare/98a2e81757f221bd12216b5dd4cf8ce340d3164c...v0.2.2)

**Closed issues:**

- Incorrect size being sent to ffmpeg [\#102](https://github.com/Zulko/moviepy/issues/102)
- Can't unlink file after audio extraction [\#97](https://github.com/Zulko/moviepy/issues/97)
- Hangs if using ImageMagick to write\_gif [\#93](https://github.com/Zulko/moviepy/issues/93)
- Segfault for import moviepy.editor, but not for import moviepy [\#92](https://github.com/Zulko/moviepy/issues/92)
- Is there a way to create the gif faster? [\#88](https://github.com/Zulko/moviepy/issues/88)
- syntax error with moviepy [\#87](https://github.com/Zulko/moviepy/issues/87)
- Issue in config.py [\#83](https://github.com/Zulko/moviepy/issues/83)
- not working with some youtube videos [\#82](https://github.com/Zulko/moviepy/issues/82)
- Can't add Chinese text 中文, it will become "??" in the movie file. [\#79](https://github.com/Zulko/moviepy/issues/79)
- don't read \*.mp4 file [\#75](https://github.com/Zulko/moviepy/issues/75)
- FileNotFound VideoFileClip exception, followed all the installation instructions [\#72](https://github.com/Zulko/moviepy/issues/72)
- write\_videofile jumps [\#71](https://github.com/Zulko/moviepy/issues/71)
- Problems with complex mask [\#70](https://github.com/Zulko/moviepy/issues/70)
- supress console window of popen calls if used with cx\_freeze win32gui [\#68](https://github.com/Zulko/moviepy/issues/68)
- set all filehandles to make moviepy work in cx\_freeze win32gui [\#67](https://github.com/Zulko/moviepy/issues/67)
- Setting conf.py ffmpeg path on the fly from python [\#66](https://github.com/Zulko/moviepy/issues/66)
- gif\_writers.py uses an undefined constant [\#64](https://github.com/Zulko/moviepy/issues/64)
- set\_duration ignored on TextClip [\#63](https://github.com/Zulko/moviepy/issues/63)
- Write\_Gif returns errno 2 [\#62](https://github.com/Zulko/moviepy/issues/62)
- "Bad File Descriptor" when creating VideoFileClip [\#61](https://github.com/Zulko/moviepy/issues/61)
- Create a mailing list [\#59](https://github.com/Zulko/moviepy/issues/59)
- Closing VideoFileClip [\#57](https://github.com/Zulko/moviepy/issues/57)
- TextClips can cause an Exception if the text argument starts with a '@' [\#56](https://github.com/Zulko/moviepy/issues/56)
- Cannot convert mov to gif [\#55](https://github.com/Zulko/moviepy/issues/55)
- Problem with writing audio [\#51](https://github.com/Zulko/moviepy/issues/51)
- ffmpeg\_writer.py [\#50](https://github.com/Zulko/moviepy/issues/50)
- VideoFileClip error [\#49](https://github.com/Zulko/moviepy/issues/49)
- VideoFileClip opens file with wrong width [\#48](https://github.com/Zulko/moviepy/issues/48)
- Change speed of clip based on a curve? [\#46](https://github.com/Zulko/moviepy/issues/46)
- 'to\_gif' raises IOError/OSError when no 'program' parameter is given [\#43](https://github.com/Zulko/moviepy/issues/43)
- Enhancement: loading animated gifs, passing frame range to subclip\(\) [\#40](https://github.com/Zulko/moviepy/issues/40)
- ImageClip is broken [\#39](https://github.com/Zulko/moviepy/issues/39)
- Error: wrong indices in video buffer. Maybe buffer too small. [\#38](https://github.com/Zulko/moviepy/issues/38)
- It makes pygame crash [\#37](https://github.com/Zulko/moviepy/issues/37)
- Can not load the fonts [\#36](https://github.com/Zulko/moviepy/issues/36)
- Tabs in python code [\#35](https://github.com/Zulko/moviepy/issues/35)
- Windows 8 Error [\#34](https://github.com/Zulko/moviepy/issues/34)
- infinite audio loop [\#33](https://github.com/Zulko/moviepy/issues/33)
- Specifying pix\_fmt on FFMPEG call [\#27](https://github.com/Zulko/moviepy/issues/27)
- on\_color fails with TypeError when given a col\_opacity parameter [\#25](https://github.com/Zulko/moviepy/issues/25)
-  'ValueError: I/O operation on closed file' [\#23](https://github.com/Zulko/moviepy/issues/23)
- Too stupid to rotate :D [\#22](https://github.com/Zulko/moviepy/issues/22)
- FFMPEG Error on current Debian Wheezy x64 [\#21](https://github.com/Zulko/moviepy/issues/21)
- Possible memory leak [\#18](https://github.com/Zulko/moviepy/issues/18)
- Windows - Unable to export simple sequence to gif [\#16](https://github.com/Zulko/moviepy/issues/16)
- Problems with preview + missing explanation of crop + resize not working [\#15](https://github.com/Zulko/moviepy/issues/15)
- AssertionError in ffmpeg\_reader.py [\#14](https://github.com/Zulko/moviepy/issues/14)
- ffmpeg hangs [\#13](https://github.com/Zulko/moviepy/issues/13)
- Python 3.3.3 - invalid syntax error [\#12](https://github.com/Zulko/moviepy/issues/12)
- something went wrong with the audio writing, Exit code 1 [\#10](https://github.com/Zulko/moviepy/issues/10)
- `error: string:` When trying to import from moviepy [\#9](https://github.com/Zulko/moviepy/issues/9)
- Reading video on Ubuntu 13.10 does not work [\#8](https://github.com/Zulko/moviepy/issues/8)
- List decorator and pygame as dependencies on PyPI [\#4](https://github.com/Zulko/moviepy/issues/4)
- "list index out of range" error or Arch Linux x86-64 [\#3](https://github.com/Zulko/moviepy/issues/3)
- IndexError? [\#2](https://github.com/Zulko/moviepy/issues/2)
- Can't write a movie with default codec [\#1](https://github.com/Zulko/moviepy/issues/1)

**Merged pull requests:**

- - changed none to None due to NameError [\#95](https://github.com/Zulko/moviepy/pull/95) ([Eloar](https://github.com/Eloar))
- Fix a typo in a ValueError message [\#91](https://github.com/Zulko/moviepy/pull/91) ([naglis](https://github.com/naglis))
- Changed all "== None" and "!= None" [\#89](https://github.com/Zulko/moviepy/pull/89) ([diegocortassa](https://github.com/diegocortassa))
- 'Crop' fix [\#81](https://github.com/Zulko/moviepy/pull/81) ([ccarlo](https://github.com/ccarlo))
- fix lost threads parameter from merge [\#78](https://github.com/Zulko/moviepy/pull/78) ([bobatsar](https://github.com/bobatsar))
- VideoClip.write\_videofile\(\) accepts new param: ffmpeg\_params that is put directly into ffmpeg command line [\#77](https://github.com/Zulko/moviepy/pull/77) ([aherok](https://github.com/aherok))
- make compatible with cx\_freeze in gui32 mode [\#69](https://github.com/Zulko/moviepy/pull/69) ([bobatsar](https://github.com/bobatsar))
- Fix typo in error message [\#53](https://github.com/Zulko/moviepy/pull/53) ([mekza](https://github.com/mekza))
- Fixed write\_logfile/verbose arguments [\#47](https://github.com/Zulko/moviepy/pull/47) ([KyotoFox](https://github.com/KyotoFox))
- typo [\#42](https://github.com/Zulko/moviepy/pull/42) ([tasinttttttt](https://github.com/tasinttttttt))
- Tempfile [\#31](https://github.com/Zulko/moviepy/pull/31) ([dimatura](https://github.com/dimatura))
- Fixed small typo in docs [\#30](https://github.com/Zulko/moviepy/pull/30) ([dimatura](https://github.com/dimatura))
- Fixed syntax error in io/imageMagick\_tools.py [\#29](https://github.com/Zulko/moviepy/pull/29) ([dimatura](https://github.com/dimatura))
- added -pix\_fmt yuv420p to ffmpeg args if codec is libx264 [\#28](https://github.com/Zulko/moviepy/pull/28) ([chunder](https://github.com/chunder))
- added support for aac audio codec [\#26](https://github.com/Zulko/moviepy/pull/26) ([chunder](https://github.com/chunder))
- Hopefully fixes issue \#13 for everyone. [\#24](https://github.com/Zulko/moviepy/pull/24) ([oxivanisher](https://github.com/oxivanisher))
- Reduced ffmpeg logging to prevent hanging [\#20](https://github.com/Zulko/moviepy/pull/20) ([JoshdanG](https://github.com/JoshdanG))
- fix typo in close\_proc [\#17](https://github.com/Zulko/moviepy/pull/17) ([kenchung](https://github.com/kenchung))
- PEP8 : ffmpeg\_reader [\#11](https://github.com/Zulko/moviepy/pull/11) ([tacaswell](https://github.com/tacaswell))
- Update resize.py [\#7](https://github.com/Zulko/moviepy/pull/7) ([minosniu](https://github.com/minosniu))
- Update crash\_course.rst [\#5](https://github.com/Zulko/moviepy/pull/5) ([mgaitan](https://github.com/mgaitan))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
