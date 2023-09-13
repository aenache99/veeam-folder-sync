#!/usr/bin/python3

""" The tests for the Folder Sync module.

Currently, it has 11 tests that assess the functionality of the module."""

import os
import shutil
import time
import pytest
from main import copy_changed_files, create_missing_directory, \
    remove_extra_files, remove_extra_directory, synchronize

# Test data
test_source_path = "test_data/source"
test_replica_path = "test_data/replica"


@pytest.fixture
def setup_test_folders(tmpdir):
    """Create test folders and files"""
    os.makedirs(test_source_path, exist_ok=True)
    os.makedirs(test_replica_path, exist_ok=True)
    with open(os.path.join(test_source_path, "file1.txt"), "w") as f:
        f.write("Hello, World!")
    yield
    shutil.rmtree(test_source_path)
    shutil.rmtree(test_replica_path)


def test_copy_changed_files(setup_test_folders):
    copy_changed_files(os.path.join(test_source_path, "file1.txt"),
                       os.path.join(test_replica_path, "file1.txt"))
    assert os.path.exists(os.path.join(test_replica_path, "file1.txt"))


def test_create_missing_directory(setup_test_folders):
    create_missing_directory(os.path.join(test_replica_path, "subfolder"))
    assert os.path.exists(os.path.join(test_replica_path, "subfolder"))


def test_remove_extra_files(setup_test_folders):
    with open(os.path.join(test_replica_path, "extra_file.txt"), "w") as f:
        f.write("This is an extra file.")
    remove_extra_files(os.path.join(test_replica_path, "extra_file.txt"))
    assert not os.path.exists(os.path.join(test_replica_path, "extra_file.txt"))


def test_remove_extra_directory(setup_test_folders):
    os.makedirs(os.path.join(test_replica_path, "extra_folder"))
    remove_extra_directory(os.path.join(test_replica_path, "extra_folder"))
    assert not os.path.exists(os.path.join(test_replica_path, "extra_folder"))


def test_synchronize(setup_test_folders):
    synchronize(test_source_path, test_replica_path)
    assert os.path.exists(os.path.join(test_replica_path, "file1.txt"))


def test_copy_changed_files_not_modified(setup_test_folders):
    # Copy the initial file
    copy_changed_files(os.path.join(test_source_path, "file1.txt"),
                       os.path.join(test_replica_path, "file1.txt"))

    # Sleep to ensure file modification time is different
    time.sleep(1)

    # Copy again, the file hasn't been modified, so it shouldn't be copied
    copy_changed_files(os.path.join(test_source_path, "file1.txt"),
                       os.path.join(test_replica_path, "file1.txt"))

    # Assert that the file still exists in replica path
    assert os.path.exists(os.path.join(test_replica_path, "file1.txt"))


def test_copy_changed_files_modified(setup_test_folders):
    # Modify the file, should trigger copy
    with open(os.path.join(test_source_path, "file1.txt"), "w") as f:
        f.write("Modified content.")
    copy_changed_files(os.path.join(test_source_path, "file1.txt"),
                       os.path.join(test_replica_path, "file1.txt"))
    assert os.path.exists(os.path.join(test_replica_path, "file1.txt"))


def test_synchronize_removed_file(setup_test_folders):
    # Test syncing after file removal
    os.remove(os.path.join(test_source_path, "file1.txt"))
    synchronize(test_source_path, test_replica_path)
    assert not os.path.exists(os.path.join(test_replica_path, "file1.txt"))


def test_create_missing_directory_already_exists(setup_test_folders):
    # Test creating an existing directory, should not raise an error
    create_missing_directory(os.path.join(test_replica_path, "subfolder"))
    assert os.path.exists(os.path.join(test_replica_path, "subfolder"))


def test_synchronize_empty_folders(setup_test_folders):
    # Test syncing empty source and replica folders
    empty_source_path = os.path.join(test_source_path, "empty_source")
    os.makedirs(empty_source_path)
    synchronize(empty_source_path, test_replica_path)
    assert os.listdir(test_replica_path) == []


def test_synchronize_with_subdirectories(setup_test_folders):
    # Test syncing source with subdirectories
    os.makedirs(os.path.join(test_source_path, "subdir1"))
    os.makedirs(os.path.join(test_source_path, "subdir2"))
    with open(os.path.join(test_source_path, "subdir1", "file2.txt"), "w") as f:
        f.write("Subdirectory file content.")

    # Create subdirectories in replica path
    os.makedirs(os.path.join(test_replica_path, "subdir1"))
    os.makedirs(os.path.join(test_replica_path, "subdir2"))

    # Run the synchronization
    synchronize(test_source_path, test_replica_path)

    assert os.path.exists(os.path.join(test_replica_path, "subdir1", "file2.txt"))


if __name__ == "__main__":
    pytest.main()
