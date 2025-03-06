import argparse
from pathlib import Path
import sys
from pprint import pprint
sys.path.append(str(Path(__file__).parent.parent))
import pycloudshare

def get_args():
    parser = argparse.ArgumentParser(description='Manage CloudShare environments')
    parser.add_argument('command', choices=['list', 'create', 'delete'])
    parser.add_argument('env_name', nargs='?', default=None)
    return parser.parse_args()

def main():
    csc = pycloudshare.CloudShareClassic()
    csa = pycloudshare.CloudShareAccelerate()

    projects = csc.get_projects()
    pprint(projects)

if __name__ == '__main__':
    main()
