"""The Folder Sync Python module:

It utilizes only 1st party Python libraries (sans the PyTest and PyLint libraries).

It implements a Folder Synchronization module as of VEEAM's specifications.

Besides the specifications, multiple things have been taken into consideration:

- The CLI arguments are given using position-independent named arguments,
- Exception handling for various situations, such as interval being
set to 0, Permission errors or the absence of the Source folder.
- The code was broken into multiple functions, for ease of
development and reading.

And besides those mentioned, some other aspects were implemented as well:

- Version Control integration to GitHub through the PyCharm IDE
- Linting with PyLint, to enforce a cohesive coding style
- Creation of a Dockerfile, in order for the project to be passed through a CI pipeline in
my personal GitHub repo and a possible deployment to a K8s engine like GKE
- Usage of PyTest in order to ensure good testing practices.
- Created a CI pipeline using GitHub Actions to automate the
Linting and Testing processes, in order to ensure quality code is being provided
in the event of working in an Agile team.
"""

import os
import shutil
import time
import argparse
import logging


def setup_logging(log_path):
    """A function meant for setting up the logging"""
    logging.basicConfig(filename=log_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logging.getLogger('').addHandler(console_handler)


def copy_changed_files(source_filepath, replica_filepath):
    """A function meant for copying changed files"""
    try:
        if (not os.path.exists(replica_filepath) or
                os.path.getmtime(source_filepath) > os.path.getmtime(replica_filepath)):
            shutil.copy2(source_filepath, replica_filepath)
            logging.info("Copied %s to %s", source_filepath, replica_filepath)
    except PermissionError as permission_error:
        logging.error("Error while copying %s to %s: %s",
                      source_filepath, replica_filepath, permission_error)


def create_missing_directory(replica_dirpath):
    """A function meant for creating the missing replica directory"""
    try:
        if not os.path.exists(replica_dirpath):
            os.makedirs(replica_dirpath)
            logging.info("Created directory %s", replica_dirpath)
    except PermissionError as permission_error:
        logging.error("Error while creating directory %s: %s", replica_dirpath, permission_error)


def remove_extra_files(replica_filepath):
    """A function meant for removing the extra files"""
    try:
        os.remove(replica_filepath)
        logging.info("Removed file %s", replica_filepath)
    except PermissionError as permission_error:
        logging.error("Error while removing file %s: %s", replica_filepath, permission_error)


def remove_extra_directory(replica_dirpath):
    """A function meant for removing the extra directory"""
    try:
        shutil.rmtree(replica_dirpath)
        logging.info("Removed directory %s", replica_dirpath)
    except PermissionError as permission_error:
        logging.error("Error while removing directory %s: %s", replica_dirpath, permission_error)


def synchronize(source_path, replica_path):
    """Here we perform the actual folder syncing, taking advantage of the functions created above"""
    for dirpath, dirnames, filenames in os.walk(replica_path, topdown=False):
        for filename in filenames:
            replica_filepath = os.path.join(dirpath, filename)
            source_filepath = (os.path.join
                               (source_path, os.path.relpath(replica_filepath, replica_path)))

            if not os.path.exists(source_filepath):
                remove_extra_files(replica_filepath)

        for dirname in dirnames:
            replica_dirpath = os.path.join(dirpath, dirname)
            source_dirpath = (os.path.join
                              (source_path, os.path.relpath(replica_dirpath, replica_path)))

            if not os.path.exists(source_dirpath):
                remove_extra_directory(replica_dirpath)

    for dirpath, dirnames, filenames in os.walk(source_path):
        for dirname in dirnames:
            replica_dirpath = os.path.join(dirpath, dirname)
            source_dirpath = (os.path.join
                              (source_path, os.path.relpath(replica_dirpath, replica_path)))

            create_missing_directory(replica_dirpath)

        for filename in filenames:
            source_filepath = os.path.join(dirpath, filename)
            replica_filepath = (os.path.join
                                (replica_path, os.path.relpath(source_filepath, source_path)))

            copy_changed_files(source_filepath, replica_filepath)


def main():
    """Takes in the arguments required for syncing"""
    parser = argparse.ArgumentParser(description="Synchronize two folders")
    parser.add_argument("-s", "--source", dest="source_path", required=True,
                        help="path to source folder")
    parser.add_argument("-r", "--replica", dest="replica_path", required=True,
                        help="path to replica folder")
    parser.add_argument("-l", "--log", dest="log_path", required=True,
                        help="path to log file")
    parser.add_argument("-i", "--interval", dest="interval", type=int, required=True,
                        help="synchronization interval in seconds")
    args = parser.parse_args()

    setup_logging(args.log_path)

    try:
        if not os.path.exists(args.source_path):
            raise FileNotFoundError(f"Source folder '{args.source_path}' doesn't exist!")

        if args.interval == 0:
            raise ValueError("Synchronization interval cannot be 0!")

        if not os.access(args.source_path, os.R_OK) or not os.access(args.replica_path, os.W_OK):
            raise PermissionError("Insufficient permissions for source or replica folder!")

        time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logging.info("Synchronization started at %s with an interval of %s seconds",
                     time_now, args.interval)
        while True:
            synchronize(args.source_path, args.replica_path)
            logging.info("Source folder %s and replica folder %s have been successfully synchronized at %s",
                         args.source_path, args.replica_path,
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(args.interval)
    except FileNotFoundError as e:
        logging.error(str(e))
    except PermissionError as e:
        logging.error(str(e))
    except ValueError as e:
        logging.error(str(e))
    except KeyboardInterrupt:
        logging.info("The user has interrupted the synchronization.")


if __name__ == "__main__":
    main()
