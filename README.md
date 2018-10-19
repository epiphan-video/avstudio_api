# AV Studio API

This repo contains:

- `/avstudio`: Python wrapper for AV Studio API
- `/docs`: API reference
- `/device_api.ipynb`: Python notebook with API tutorial
- `/device_api.html`: static version of the tutorial

## Installation

```
$ git clone https://github.com/epiphan-video/avstudio_api.git
$ cd avstudio_api
$ pip install -r
```

## Running the interactive tutorial

Jupyter has to be installed.

```
$ cd avstudio_api
$ python -m notebook
```

## Documentation

API documentation is available via Github Pages: [https://epiphan-video.github.io/avstudio_api](https://epiphan-video.github.io/avstudio_api/)


### How to update docs

Documentation source is stored in `docs-source-slate` folder.

1) Build a slate builder container (once):

```shell
$ cd slate
$ build -t slate-builder .
```

2) Then use the container to build docs:

```bash
docker run -it --rm -v $(pwd)/docs-source-slate/:/slate/source -v $(pwd)/docs:/slate/build slate-builder
```

This command will update files in `docs` folder, if necessary.

3) git commit and push

