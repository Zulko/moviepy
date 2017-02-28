import pytest
import moviepy.tools as tools
import sys
import time

## taken from PR #121   (grimley517)


def test_ext():
    '''Test for find_extension function'''
    lefts = ['libx264', 'libmpeg4', 'libtheora', 'libvpx']
    rights = ['mp4', 'mp4', 'ogv', 'webm']
    for i in range(len(lefts)):
        left = tools.find_extension(lefts[i])
        right = rights[i]
        message = "{0} did not get associated with {1}".format(left, right)
        assert left == right, message

def test_2():
    '''Tests for raising erre if codec not in dictionaries'''
    message = "asking for a silly video format did not Raise a Value Error"
    with pytest.raises(ValueError, message=message):
         tools.find_extension('flashvideo')

def test_3():
    '''tests the cvsecs funtion outputs the correct times 
       as per the docstring'''
    lefts = [15.4, (1,21.5), (1,1,2), '01:01:33.5', '01:01:33.045' ]
    rights = [15.4, 81.5, 3662, 3693.5, 3693.045]
    for i in range(len(lefts)):
        left = tools.cvsecs(lefts[i])
        right = rights[i]
        message = "{0} resulted in {1}, but {2} was expected"\
            .format(lefts[i],left, right)
        assert left == right, message

def test_4():
    '''tests the is_string function in tools'''
    lefts = ["hello straight string", r'hello raw string',42, True ]
    rights = [True, True, False, False]
    for i in range(len(lefts)):
        left = tools.is_string(lefts[i])
        right = rights[i]
        message = "{0} resulted in {1}, but {2} was expected"\
            .format(lefts[i],left, right)
        assert left == right, message

def test_4a():
    '''as for test 4 - but tests for the different behaviour of byte strings
       between python 2 and 3'''
    version = sys.version_info[0]
    answer = version < 3 #True for py2, else False
    left = tools.is_string(b'hello bytes')
    right = answer
    message = "{0} resulted in {1}, but {2} was expected"\
        .format(b'hello bytes',left, right)
    assert left == right, message

def test_5():
    '''Tests for sys_write-flush function
        1) checks that this works quickly,
        2) checks that stdout has no content after flushing
    '''
    start = time.time()
    tools.sys_write_flush("hello world")
    myTime = time.time() - start
    assert myTime <  0.001
    file = sys.stdout.read()
    assert file == b""

def test_6():
    '''
        Tests subprocess_call for operation.  the process sleep should run for
        a given time in seconds. This checks that the process has 
        deallocated from the stack on completion of the called process
    '''
    process = tools.subprocess_call(["sleep" , '1'])
    time.sleep(1)
    assert process is None

if __name__ == '__main__':
   pytest.main()
