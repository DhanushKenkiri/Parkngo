"""
ParknGo Startup Wrapper
Fixes Python 3.14 protobuf compatibility issues
"""

import os
import sys

# CRITICAL: Set this BEFORE importing any modules
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# Now import and run the app
if __name__ == '__main__':
    import app
    # The app.py will handle the rest
