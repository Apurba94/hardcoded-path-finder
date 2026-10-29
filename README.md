# hardcoded-path-finder

**Find the `C:\Users\ana\Desktop\data_final.csv` and `/home/bob/project/...` lines that make
your code fail on every computer but yours, in scripts, notebooks and config files.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Hard-coded absolute paths are the single most common reason shared research code does not run
(Trisovic et al., 2022 found most R scripts in Dataverse failed, often for exactly this reason).
They also leak user names and folder structures when code is published. Replacing them with paths
relative to the project, or with configuration, is easy once you know where they are.

## Detects

| Kind | Example |
|------|---------|
| `windows-drive` | `C:\Users\ana\data.csv`, `D:/OneDrive/x.xlsx` |
| `unc-share` | `\\labserver\share\run1` |
| `unix-home` | `/home/bob/...`, `/Users/ana/...` |
| `tilde-home` | `~/data/raw.csv` |
| `mounted-volume` | `/Volumes/LabDrive`, `/mnt/data`, `/media/usb` |
| `cloud-sync` | paths inside Dropbox, OneDrive, Google Drive, iCloud |

Code files (.py, .R, .Rmd, .m, .jl and notebooks) are scanned inside string literals only, so
comments do not produce noise; config and shell files are scanned completely. URLs are ignored.

## Usage

```bash
pip install .
hardcoded-path-finder analysis/ notebooks/
hardcoded-path-finder . --summary
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
