# PDF2U

📜PDF perfect translator to you.

![help](docs/help.png)

## Install

### uv

Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### pdf2u

```bash
uv tool install pdf2u
```

## Usage

start streamlit server

```bash
pdf2u gui -a 127.0.0.1
```

upload pdf file to translate.

![upload](docs/upload.png)

translate pdf file.

![translate](docs/translate.png)
