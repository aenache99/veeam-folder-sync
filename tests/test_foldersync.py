"""
Folder Sync Test suite

Test cases can be run with the following:
    pytest test_foldersync.py
"""

import os
import shutil
import tempfile
import pytest
from main import (synchronize,
                  create_missing_directory,
                  remove_extra_files,
                  remove_extra_directory,
                  copy_changed_files)


@pytest.fixture
def temp_folder_structure():
    # Create temporary source and replica folders
    source_folder = tempfile.mkdtemp()
    replica_folder = tempfile.mkdtemp()

    # Create some test files and directories in the source folder
    os.makedirs(os.path.join(source_folder, 'dir1'))
    os.makedirs(os.path.join(source_folder, 'dir2'))
    open(os.path.join(source_folder, 'file1.txt'), 'w').close()
    open(os.path.join(source_folder, 'dir1', 'file2.txt'), 'w').close()

    yield source_folder, replica_folder

    # Clean up
    shutil.rmtree(source_folder)
    shutil.rmtree(replica_folder)


def test_create_missing_directory(temp_folder_structure):
    source_folder, replica_folder = temp_folder_structure
    replica_dirpath = os.path.join(replica_folder, 'new_dir')

    create_missing_directory(replica_dirpath)
    assert os.path.exists(replica_dirpath)


def test_remove_extra_files(temp_folder_structure):
    source_folder, replica_folder = temp_folder_structure
    replica_filepath = os.path.join(replica_folder, 'file1.txt')
    open(replica_filepath, 'w').close()

    remove_extra_files(replica_filepath)
    assert not os.path.exists(replica_filepath)


def test_remove_extra_directory(temp_folder_structure):
    source_folder, replica_folder = temp_folder_structure
    replica_dirpath = os.path.join(replica_folder, 'dir1')
    os.makedirs(replica_dirpath)

    remove_extra_directory(replica_dirpath)
    assert not os.path.exists(replica_dirpath)


def test_copy_changed_files(temp_folder_structure):
    source_folder, replica_folder = temp_folder_structure
    source_filepath = os.path.join(source_folder, 'file1.txt')
    replica_filepath = os.path.join(replica_folder, 'file1.txt')

    copy_changed_files(source_filepath, replica_filepath)
    assert os.path.exists(replica_filepath)


def test_synchronize(temp_folder_structure):
    source_folder, replica_folder = temp_folder_structure
    synchronize(source_folder, replica_folder)

    # Check if the synchronization produced the expected results
    assert sorted(os.listdir(source_folder)) == sorted(os.listdir(replica_folder))

    for root, dirs, files in os.walk(source_folder):
        for dir_name in dirs:
            source_dirpath = os.path.join(root, dir_name)
            replica_dirpath = (os.path.join
                               (replica_folder, os.path.relpath(source_dirpath, source_folder)))
            assert os.path.exists(replica_dirpath)

        for file_name in files:
            source_filepath = os.path.join(root, file_name)
            replica_filepath = (os.path.join
                                (replica_folder, os.path.relpath(source_filepath, source_folder)))
            assert os.path.exists(replica_filepath)
            assert os.path.getmtime(replica_filepath) == os.path.getmtime(source_filepath)


if __name__ == '__main__':
    pytest.main()
