import argparse
import os
import sys
import shutil

from zix.server import logging, utils


APP = "zix"
DEFAULT_LOCAL_PORT = 8000

CURRENT_DIR =  os.path.join(os.getcwd())
# This is how we get where this source file is located
CODE_DIR, _ = os.path.split(__file__)
# Use LOGGER for console output
LOGGER = logging.get_logger(logger_name=__name__)



def entry_point(working_dir=None):
    """
    Python application entry point
    1. Parse the command line arguments
    2. Define environment variables
    3. Start the server

    See the bottom of this file to find where it is invoked.
    """
    parser = argparse.ArgumentParser(APP)
    parser.add_argument(
        "command",
        type=str,
        help="init or serve",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host IP")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_LOCAL_PORT,
        help="Port",
    )
    parser.add_argument(
        "-w",
        "--working-directory",
        type=str,
        default=None,
        help="Working directory with config, static, and plugins",
    )
    parser.add_argument(
        "-e",
        "--env",
        type=str,
        default=None,
        help="environment variables in yaml",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="info",
        help="Logging level (debug, info, warning, error, critical",
    )

    # Define environment variables from the Yaml file if it is given
    args = parser.parse_args()
    if args.env:
        utils.define_env_vars_from_yaml(args.env)

    # When run in a dev mode with `python -m zix` with no -w option, the working directory is zix/default_project
    # -w option overwrides the above.
    # If not dev mode and -w is not set, the current direcctory (os.getcwd()) is the working directory
    if args.working_directory:
        working_dir = args.working_directory
    if not working_dir:
        working_dir = os.getcwd()

    if args.command in ["serve", "server"]:
        server(args.host, args.port, working_dir, args.log_level)
    elif args.command == "init":
        init_project(working_dir)
    else:
        LOGGER.error(args.command + " is an unrecognized command!")

def server(
    host:str="0.0.0.0",
    port:int=DEFAULT_LOCAL_PORT,
    working_dir=os.getcwd(),
    log_level:str="info",
    **kwargs):
    """
    Start a ASGI server with Unicorn (https://www.uvicorn.org )
    Point the browser to https://0.0.0.0:8000 after the server starts.
    """
    import uvicorn
    if working_dir:
        os.chdir(working_dir)
    wd = os.getcwd()
    LOGGER.info(f"Current directory is {wd}")
    LOGGER.info(f"Starting server at port {port}")
    LOGGER.info(f"Log level: {log_level}")
    uvicorn.run(
        APP + ".server.main:app",  # This points to "app" FastAPI object in main.py under server directory
        reload=True,
        reload_dirs=[CODE_DIR],
        host=host,
        port=port,
        log_level=log_level,
    )


def init_project(working_dir:str="."):
    sys.stdout.write(f"I'll populate the app default files to {working_dir}. Is this OK? (y/N): ")
    res = input()
    if res != "y":
        print("bye!")
        return
    shutil.copytree(os.path.join(CODE_DIR, "default_project"), working_dir)
    LOGGER.info("Default project files created.")
