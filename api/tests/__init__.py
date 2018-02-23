import sys
import os
# fix test paths (just in case)
os.environ['FLASK_TESTING'] = '1'
package_path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(package_path)