import unittest
import moviepy.tools as tools
import sys

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_1(self):
        '''Test for find_extension function'''
        lefts = ['libx264', 'libmpeg4', 'libtheora', 'libvpx']
        rights = ['mp4', 'mp4', 'ogv', 'webm']
        for i in range(len(lefts)):
            left = tools.find_extension(lefts[i])
            right = rights[i]
            message = "{0} did not get associated with {1}".format(left, right)
            self.assertEqual(left, right, msg = message)
    
    def test_2(self):
        '''Tests for raising erre if codec not in dictionaries'''
        message = "asking for a silly video format did not Raise a Value Error"
        with self.assertRaises(ValueError, msg = message):
            tools.find_extension('flashvideo')
    
    def test_3(self):
        '''tests the cvsecs funtion outputs the correct times 
        as per the docstring'''
        lefts = [15.4, (1,21.5), (1,1,2), '01:01:33.5', '01:01:33.045' ]
        rights = [15.4, 81.5, 3662, 3693.5, 3693.045]
        for i in range(len(lefts)):
            left = tools.cvsecs(lefts[i])
            right = rights[i]
            message = "{0} resulted in {1}, but {2} was expected"\
            .format(lefts[i],left, right)
            self.assertEqual(left, right, msg = message)
    
    def test_4(self):
        '''tests the is_string function in tools'''
        lefts = ["hello straight string", r'hello raw string',42, True ]
        rights = [True, True, False, False]
        for i in range(len(lefts)):
            left = tools.is_string(lefts[i])
            right = rights[i]
            message = "{0} resulted in {1}, but {2} was expected"\
            .format(lefts[i],left, right)
            self.assertEqual(left, right, msg = message)
    
    def test_4a(self):
        '''as for test 4 - but tests for the different behaviour of byte strings
        between python 2 and 3'''
        version = sys.version_info[0]
        answer = version < 3 #True for py2, else False
        left = tools.is_string(b'hello bytes')
        right = answer
        message = "{0} resulted in {1}, but {2} was expected"\
        .format(b'hello bytes',left, right)
        self.assertEqual(left, right, msg = message)
    
if __name__ == '__main__':
    unittest.main(verbosity = 3)
