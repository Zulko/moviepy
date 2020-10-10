import pytest
import sys

if len(sys.argv) > 2:
    pytest.main(["tests/" + sys.argv[1], "-k", sys.argv[2]])
elif len(sys.argv) > 1:
    pytest.main(["tests/" + sys.argv[1]])
else:
    pytest.main()
