"""The Folder Sync Python module"""

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
    except Exception as e:
        logging.error("Error while copying %s to %s: %s", source_filepath, replica_filepath, e)


def create_missing_directory(replica_dirpath):
    """A function meant for creating the missing directory"""
    try:
        if not os.path.exists(replica_dirpath):
            os.makedirs(replica_dirpath)
            logging.info("Created directory %s", replica_dirpath)
    except Exception as e:
        logging.error("Error while creating directory %s: %s", replica_dirpath, e)


def remove_extra_files(replica_filepath):
    """A function meant for removing the extra files"""
    try:
        os.remove(replica_filepath)
        logging.info("Removed file %s", replica_filepath)
    except Exception as e:
        logging.error("Error while removing file %s: %s", replica_filepath, e)


def remove_extra_directory(replica_dirpath):
    """A function meant for removing the extra directory"""
    try:
        shutil.rmtree(replica_dirpath)
        logging.info("Removed directory %s", replica_dirpath)
    except Exception as e:
        logging.error("Error while removing directory %s: %s", replica_dirpath, e)


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
    parser.add_argument("--source", dest="source_path", required=True,
                        help="path to source folder")
    parser.add_argument("--replica", dest="replica_path", required=True,
                        help="path to replica folder")
    parser.add_argument("--log", dest="log_path", required=True,
                        help="path to log file")
    parser.add_argument("--interval", dest="interval", type=int, required=True,
                        help="synchronization interval in seconds")
    args = parser.parse_args()

    setup_logging(args.log_path)

    try:
        while True:
            time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            logging.info("Synchronization started at %s", time_now)
            synchronize(args.source_path, args.replica_path)
            logging.info("Synchronization ended at %s",
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("Synchronization process interrupted by user")


if __name__ == "__main__":
    main()
