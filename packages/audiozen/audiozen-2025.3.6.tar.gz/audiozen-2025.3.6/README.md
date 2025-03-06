---
license: mit
language:
- en
pipeline_tag: audio-to-audio
---
# AudioZEN

## Prerequisites

```bash
# Install uv for speed up virtual environment creation and management
uv venv -p 3.12 venv/torch251_cu124_py312
source venv/torch251_cu124_py312/bin/activate

# Install the package
uv pip install -e .

# cd to the model directory
uv pip install -r /path/to/requirements.txt
```

## Features

- [x] Gradient accumulation
- [x] Multi-node training
- [x] BF16 support
- [x] Learning rate warmup
- [x] Learning rate decay
  - [x] Linear decay

## Prerequisites

```shell
rsync -avPxH --no-g --chmod=Dg+ /home/xhao/proj/audiozen xhao@10.21.4.91:/home/xhao/proj/audiozen --exclude="*.git" --exclude="*.egg-info" --exclude="*.egg" --exclude="*.pyc" --exclude="*.log" --exclude="*.npy"
```

- How to split the repo into read-only standalone repos? Check out [Monorepo-Management](https://github.com/haoxiangsnr/audiozen/wiki/Monorepo-Management)

## Git LFS

If files are too large and/or change frequently, consider using [Git LFS](https://git-lfs.github.com/).

```shell
git lfs install
git lfs track "*..."
git add .gitattributes
```

For ipynb files, we don't need to track them as they are not large files and they are not changed frequently.

## Publish

```shell
# Bump the version to the next CalVer
# bump-my-version will automatically update the version ids in pyproject.toml and __init__.py
bump-my-version bump patch

# Publish the package
rm -rf dist/ && uv build && uv publish

# Input the username and password
username: __token__
password: <token> in ~/.pypirc
```

## How to Process Data Files

1. 优先考虑将数据上传到 Github Release，然后在 `/path/to/local/data` 目录中下载数据
2. 在 `/path/to/local/data` 目录中创建 `README.md` 文件，描述数据的来源和下载位置