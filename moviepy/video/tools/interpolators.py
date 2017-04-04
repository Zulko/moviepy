"""
Classes for easy interpolation of trajectories and Curves.
Requires Scipy installed.
"""

import numpy as np

class Interpolator:
    """ Poorman's linear interpolator, doesn't require Scipy. """
    
    def __init__(self, tt=None, ss=None, ttss = None, left=None, right=None):

        if ttss is not None:
            tt, ss = zip(*ttss)
        
        self.tt = 1.0*np.array(tt)
        self.ss = 1.0*np.array(ss)
        self.left = left
        self.right = right
        self.tmin, self.tmax = min(tt), max(tt)

    def __call__(self, t):
        return np.interp(t, self.tt, self.ss, self.left, self.right)

class Trajectory:

    def __init__(self, tt, xx, yy):

        self.tt = 1.0*np.array(tt)
        self.xx = np.array(xx)
        self.yy = np.array(yy)
        self.update_interpolators()

    def __call__(self, t):
        return np.array([self.xi(t), self.yi(t)])

    def addx(self, x):
        return Trajectory(self.tt, self.xx+x, self.yy)

    def addy(self, y):
        return Trajectory(self.tt, self.xx, self.yy+y)

    def update_interpolators(self):
        self.xi =  Interpolator(self.tt, self.xx)
        self.yi =  Interpolator(self.tt, self.yy)
    
    def txy(self, tms=False):
        return zip((1000 if tms else 1)*self.tt, self.xx, self.yy)

    def to_file(self, filename):
        np.savetxt(filename, np.array(self.txy(tms=True)),
                   fmt="%d", delimiter='\t')

    @staticmethod
    def from_file(filename):
        arr = np.loadtxt(filename, delimiter='\t')
        tt, xx, yy = arr.T
        return Trajectory(1.0*tt/1000, xx, yy)

    @staticmethod
    def save_list(trajs, filename):
        N = len(trajs)
        arr = np.hstack([np.array(list(t.txy(tms=True))) for t in trajs])
        np.savetxt( filename, arr, fmt="%d", delimiter='\t',
                    header = "\t".join(N*['t(ms)', 'x', 'y']))
    
    @staticmethod
    def load_list(filename):
        arr = np.loadtxt(filename, delimiter='\t').T
        Nlines = arr.shape[0]
        return [Trajectory(tt=1.0*a[0]/1000, xx=a[1], yy=a[2])
                for a in np.split(arr, Nlines/3)]
