def lum_contrast(clip, lum=0, contrast=0, contrast_threshold=127):
    """Luminosity-contrast correction of a clip."""

    def image_filter(im):
        im = 1.0 * im  # float conversion
        corrected = im + lum + contrast * (im - float(contrast_threshold))
        corrected[corrected < 0] = 0
        corrected[corrected > 255] = 255
        return corrected.astype("uint8")

    return clip.image_transform(image_filter)
