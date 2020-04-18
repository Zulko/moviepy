import numpy as np

# Ensure that blend_modes is available, otherwise this cannot be used
try:
    from blend_modes import blend_modes
except ImportError as ex:
    msg = (
        'Using blending requires the "blend_modes" package.'
        + ' Please install with "pip install blend_modes" and try again.'
    )
    raise ImportError(msg)


def blended_blit_on(
    self, picture, t, blend_mode="normal", blend_opacity=1.0, blend_weight=1.0
):
    """
    Returns the result of the blit of the clip's frame at time `t`
    on the given `picture`, the position of the clip being given
    by the clip's ``pos`` attribute. Meant for compositing.

    Blending parameters are exposed for BlendedCompositeVideoClip,
    otherwise they are ignored.
    """
    hf, wf = framesize = picture.shape[:2]

    if self.ismask and picture.max() != 0:
        return np.minimum(1, picture + self.blit_on(np.zeros(framesize), t))

    ct = t - self.start  # clip time

    # GET IMAGE AND MASK IF ANY

    img = self.get_frame(ct)
    mask = None if (self.mask is None) else self.mask.get_frame(ct)
    if mask is not None:
        if (img.shape[0] != mask.shape[0]) or (img.shape[1] != mask.shape[1]):
            img = self.fill_array(img, mask.shape)
    hi, wi = img.shape[:2]

    # SET POSITION

    pos = self.pos(ct)

    # preprocess short writings of the position
    if isinstance(pos, str):
        pos = {
            "center": ["center", "center"],
            "left": ["left", "center"],
            "right": ["right", "center"],
            "top": ["center", "top"],
            "bottom": ["center", "bottom"],
        }[pos]
    else:
        pos = list(pos)

    # is the position relative (given in % of the clip's size) ?
    if self.relative_pos:
        for i, dim in enumerate([wf, hf]):
            if not isinstance(pos[i], str):
                pos[i] = dim * pos[i]

    if isinstance(pos[0], str):
        D = {"left": 0, "center": (wf - wi) / 2, "right": wf - wi}
        pos[0] = D[pos[0]]

    if isinstance(pos[1], str):
        D = {"top": 0, "center": (hf - hi) / 2, "bottom": hf - hi}
        pos[1] = D[pos[1]]

    pos = map(int, pos)

    result = blended_blit(
        img,
        picture,
        pos,
        mask=mask,
        ismask=self.ismask,
        blend_mode=blend_mode,
        blend_opacity=blend_opacity,
        blend_weight=blend_weight,
    )
    return result


def blended_blit(
    im1,
    im2,
    pos=None,
    mask=None,
    ismask=False,
    blend_mode="normal",
    blend_opacity=1.0,
    blend_weight=1.0,
):
    """ Blit an image over another.

    Blits ``im1`` on ``im2`` as position ``pos=(x,y)``, using the
    ``mask`` if provided. If ``im1`` and ``im2`` are mask pictures
    (2D float arrays) then ``ismask`` must be ``True``.

    By default, and if the blend_modes package is not installed, ``im1`` will
    be follow the "normal" blend mode, see
    https://en.wikipedia.org/wiki/Blend_modes#Normal_blend_mode

    If blend_modes is installed, then any of the blend_modes can be used. There
    are two additional parameters which can be used to fine-tune the output:
    ``blend_opacity`` (float, [0,1]) the opacity that is passed through
    to the blend_mode
    ``blend_weight`` (float, [0,1]) allows for combining a blend_mode with
    the "normal" blend mode, which is useful for layers that can end up
    looking dark. A value of 1 corresponds to using blend_mode fully and a
    value of 0 corresponds to using "normal" fully.
    """

    def _blend_normal(mask, blitted, blit_region):
        return (1.0 * mask * blitted) + ((1.0 - mask) * blit_region)

    if pos is None:
        pos = [0, 0]

    # xp1,yp1,xp2,yp2 = blit area on im2
    # x1,y1,x2,y2 = area of im1 to blit on im2
    xp, yp = pos
    x1 = max(0, -xp)
    y1 = max(0, -yp)
    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    xp2 = min(w2, xp + w1)
    yp2 = min(h2, yp + h1)
    x2 = min(w1, w2 - xp)
    y2 = min(h1, h2 - yp)
    xp1 = max(0, xp)
    yp1 = max(0, yp)

    if (xp1 >= xp2) or (yp1 >= yp2):
        return im2

    blitted = im1[y1:y2, x1:x2]

    new_im2 = +im2

    if mask is not None:
        mask = mask[y1:y2, x1:x2]
        if len(im1.shape) == 3:
            mask = np.dstack(3 * [mask])
        blit_region = new_im2[yp1:yp2, xp1:xp2]

        # Sanity check on inputs
        blend_mode = blend_mode.strip().lower()
        blend_opacity = max(min(abs(blend_opacity), 1.0), 0.0)
        blend_weight = max(min(abs(blend_weight), 1.0), 0.0)
        if blend_mode == "normal":
            new_im2[yp1:yp2, xp1:xp2] = _blend_normal(mask, blitted, blit_region)
        else:
            # Arrays are converted to be four-dimensional since blend_modes
            # works with the alpha-channel for the blending
            # For now assume all background (im2) to be visible
            background = np.ones(
                (blit_region.shape[0], blit_region.shape[1], 4), dtype="float"
            )
            background[:, :, :3] = blit_region

            # Layer / im1
            layer = np.zeros(
                (blit_region.shape[0], blit_region.shape[1], 4), dtype="float"
            )
            layer[:, :, :3] = blitted
            # Mask is duplicated across channels above, so just take the first
            layer[:, :, 3] = mask[:, :, 0]

            # Defer the blending calculations to blend_modes package
            try:
                blend_method = getattr(blend_modes, blend_mode)
                blended = blend_method(background, layer, blend_opacity)
            except AttributeError:
                blended = _blend_normal(mask, blitted, blit_region)

            # Combine if non-unity blend_weight
            if blend_weight < 1.0:
                blended *= blend_weight
                blended[:, :, :3] += (1.0 - blend_weight) * _blend_normal(
                    mask, blitted, blit_region
                )

            # Update the relevant part of new_im2
            new_im2[yp1:yp2, xp1:xp2] = blended[:, :, :3]

    else:
        new_im2[yp1:yp2, xp1:xp2] = blitted

    return new_im2.astype("uint8") if (not ismask) else new_im2
