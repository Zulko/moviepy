"""
Classes for easy interpolation of trajectories and Curves.
Requires Scipy installed.
"""

import numpy as np

class Interpolator:
    """ Poorman's linear interpolator, doesn't require Scipy. """
    
    def __init__(self, tt, ss, left=None, right=None):
        
        self.tt = 1.0*np.array(tt)
        self.ss = 1.0*np.array(ss)
        self.left = ss[0] if (left is None) else left
        self.right = ss[-1] if (right is None) else right
        self.tmin, self.tmax = min(tt), max(tt)

    def __call__(self, t):
        if (t <= self.tmin):
            return self.left
        if (t >= self.tmax):
            return self.right
        ind = np.argmax(np.diff(self.tt >= t)==1)
        t1, t2 = self.tt[ind], self.tt[ind+1]
        s1, s2 = self.ss[ind], self.ss[ind+1]
        return s1 + (s2-s1)*(t-t1)/(t2-t1)



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

        return Trajectory(self.tt, self.xx+y, self.yy)

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
        arr = np.hstack([np.array(t.txy(tms=True)) for t in trajs])
        np.savetxt( filename, arr, fmt="%d", delimiter='\t',
                    header = "\t".join(N*['t (ms)', 'x', 'y']))
    
    @staticmethod
    def load_list(filename):

        arr = np.loadtxt(filename, delimiter='\t').T
        Nlines = arr.shape[0]
        return [Trajectory(tt=1.0*a[0]/1000, xx=a[1], yy=a[2])
                for a in np.split(arr, Nlines/3)]
