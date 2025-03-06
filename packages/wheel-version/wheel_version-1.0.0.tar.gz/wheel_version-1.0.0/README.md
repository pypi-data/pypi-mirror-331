# wheel-version
A CLI tool to get versions from Python Wheel files

## Running

### Installing Python package from PyPI
```sh
pip install wheel-version
```
And then
```sh
wheel-version asdf-1.2.3-py3-none-any.whl
# OR
python3 -m wheel_version asdf-1.2.3-py3-none-any.whl
```

### Installing with `uv` / `pipx`
```sh
uv tool install wheel-version
# OR
pipx install wheel-version
```
And then
```sh
wheel-version asdf-1.2.3-py3-none-any.whl
```

### Running with `uvx` / `pipx` from PyPI
```sh
uvx wheel-version asdf-1.2.3-py3-none-any.whl
# OR
pipx run wheel-version asdf-1.2.3-py3-none-any.whl
```

### Running with `uvx` / `pipx` as single file directly from source
```sh
curl -fsSL https://github.com/zeevro/wheel-version/raw/refs/heads/main/wheel_version.py | uv run -
```

### Downloading source and running as single file with `uv` / `pipx`
```sh
wget https://github.com/zeevro/wheel-version/raw/refs/heads/main/wheel_version.py
# OR
curl -fsSLo wheel_version.py https://github.com/zeevro/wheel-version/raw/refs/heads/main/wheel_version.py
```
And then
```sh
uv run wheel_version.py
# OR
pipx run wheel_version.py
```

## Usage
Use `-h` / `--help`. I'm lazy... 😅
