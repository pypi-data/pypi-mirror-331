import logging
import os
import platform

from datetime import datetime

DEFAULT_PROJECT = "scp-file-utils"

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(__file__),
    "conf",
    "config.yaml"
)

DEFAULT_TIMESTAMP = str(datetime.today().strftime("%Y-%m-%d-%H%M%S"))

# Get the operating system
OS = platform.system()  # Use platform.system() instead of os.uname().sysname

DEFAULT_DOWNLOADS_DIR = None
DEFAULT_OUTDIR_BASE = None

# If the operating system is Windows, set the downloads directory to the user's Downloads folder
if OS == "Windows":
    DEFAULT_DOWNLOADS_DIR = os.path.join(
        os.getenv("USERPROFILE"),
        "Downloads",
    )
    DEFAULT_OUTDIR_BASE = os.path.join(
        os.getenv("USERPROFILE"),
        "Downloads",
        DEFAULT_PROJECT,
    )
# Otherwise, set the downloads directory to the user's home directory
else:
    DEFAULT_DOWNLOADS_DIR = os.path.join(
        os.getenv("HOME"),
        "Downloads",
    )
    DEFAULT_OUTDIR_BASE = os.path.join(
        "/tmp/",
        os.getenv("USER"),
        DEFAULT_PROJECT,
    )

DEFAULT_LOGGING_FORMAT = (
    "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"
)

DEFAULT_LOGGING_LEVEL = logging.INFO

DEFAULT_VERBOSE = False
