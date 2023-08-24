# veeam-folder-sync
This repository contains the files associated with the Folder Sync technical assignment written in Python.

It utilizes only 1st party Python libraries (sans the PyTest and PyLint libraries).

It implements a Folder Synchronization module as of VEEAM's specifications.

And besides those mentioned, some other aspects were implemented as well:

- Version Control integration to GitHub through the PyCharm IDE
- Linting with PyLint, to enforce a cohesive coding style
- Creation of a Dockerfile, in order for the project to be passed through a CI pipeline in
my personal GitHub repo and a possible deployment to a K8s engine like GKE
- Usage of PyTest in order to ensure good testing practices.
- Created a CI pipeline using GitHub Actions to automate the
Linting and Testing processes, in order to ensure quality code is being provided
in the event of working in an Agile team.
