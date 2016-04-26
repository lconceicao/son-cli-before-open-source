import sys
import os
import logging
import coloredlogs
from os.path import expanduser
from son.workspace.workspace import Workspace
from son.workspace.project import Project

log = logging.getLogger(__name__)


class Publisher(object):

    def __init__(self, workspace, project=None, component=None):
        self._workspace = workspace
        self._project = project
        self._component = component


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Publish a project or component to the catalogue server")
    parser.add_argument("--workspace", help="Specify workspace. Default is located at '{}'"
                        .format(Workspace.DEFAULT_WORKSPACE_DIR), required=False)
    parser.add_argument("--project",
                        help="Specify project to be published", required=False)
    parser.add_argument("--component", help="Project component to be published.", required=False)

    args = parser.parse_args()

    # Ensure that either --component or --project argument is given, but not the two simultaneously (XOR)
    if bool(args.component) == bool(args.project):
        parser.print_help()
        return

    # If workspace arg is not given, specify workspace as the default location
    if not args.workspace:
        ws_root = Workspace.DEFAULT_WORKSPACE_DIR
    else:
        ws_root = expanduser(args.workspace)

    # Create the Workspace object
    ws = Workspace.__create_from_descriptor__(ws_root)
    if not ws:
        print("Could not find a SONATA SDK workspace at '{}'".format(ws_root), file=sys.stderr)
        exit(1)

    if args.project:
        prj_root = os.path.expanduser(args.project)
        proj = Project(prj_root, ws)
        if not proj:
            print("Could not find a SONATA SDK project at '{}'".format(prj_root), file=sys.stderr)
            exit(1)
        pub = Publisher(ws, project=proj)

    if args.component:
        comp_file = os.path.expanduser(args.component)
        if not os.path.isfile(comp_file):
            print("'{}' is not a valid file".format(comp_file), file=sys.stderr)
            exit(1)
        pub = Publisher(ws, component=comp_file)
