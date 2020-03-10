import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider


def sliders(f, sliders_properties, wait_for_validation = False):
    """ A light GUI to manually explore and tune the outputs of 
        a function.
        slider_properties is a list of dicts (arguments for Slider )
        
        def volume(x,y,z):
            return x*y*z
    
        intervals = [ { 'label' :  'width',  'valmin': 1 , 'valmax': 5 },
                  { 'label' :  'height',  'valmin': 1 , 'valmax': 5 },
                  { 'label' :  'depth',  'valmin': 1 , 'valmax': 5 } ]
        inputExplorer(volume,intervals)
    """
        
    nVars = len(sliders_properties)
    slider_width = 1.0/nVars
    
    # CREATE THE CANVAS
    
    figure,ax = plt.subplots(1)
    figure.canvas.set_window_title( "Inputs for '%s'"%(f.func_name) )
    
    # choose an appropriate height
    
    width,height = figure.get_size_inches()
    height = min(0.5*nVars,8)
    figure.set_size_inches(width,height,forward = True)
    
    
    # hide the axis
    ax.set_frame_on(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    

    # CREATE THE SLIDERS
    
    sliders = []
    
    for i, properties in enumerate(sliders_properties):    
        ax = plt.axes([0.1 , 0.95-0.9*(i+1)*slider_width,
                       0.8 , 0.8* slider_width])
        if not isinstance(properties,dict):
            properties =dict(zip(['label','valmin', 'valmax', 'valinit'],
                             properties))
        sliders.append( Slider(ax=ax, **properties) )
    
    
    # CREATE THE CALLBACK FUNCTIONS
    
    def on_changed(event) :     
        res = f(*(s.val for s in sliders))
        if res is not None:
            print( res )
    
    def on_key_press(event):
        if event.key is 'enter':
            on_changed(event)   
    
    figure.canvas.mpl_connect('key_press_event', on_key_press)
    
    # AUTOMATIC UPDATE ?
    
    if not wait_for_validation:
        for s in sliders :
            s.on_changed(on_changed)
    
    
    # DISPLAY THE SLIDERS
    plt.show()
