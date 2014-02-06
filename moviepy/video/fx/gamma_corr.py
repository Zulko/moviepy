
def gamma_corr(clip, gamma):
    """ Gamma-correction of a video clip """
    def fl(im):
        corrected = (255*(1.0*im/255)**gamma)
        return corrected.astype('uint8')
    
    return clip.fl_image(fl)
