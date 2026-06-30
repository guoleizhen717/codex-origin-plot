# Origin COM automation — known issues from real-world battle testing

> This reference documents what actually works (and what crashes) when driving
> Origin via `win32com.client` in Codex. Read before writing any Origin COM code.

## tl;dr

| Action | COM Status | Workaround |
|--------|-----------|------------|
| `newproject`, `win -t wks`, fill cells | ✅ Stable | — |
| `plotxy` create graphs | ✅ Stable | — |
| `xb.text$`, `yl.text$`, `layer.x.from` | ✅ Stable | — |
| `merge_graph` | ⚠️ Sometimes False | Try in fresh session |
| `expGraph type:=png` | ❌ Returns True but **no file created** | Use `page.export` or screenshot |
| `save -i` (.opju) | ❌ Crashes COM `(-2147417851)` | Avoid; save via Origin GUI or skip |
| `doc -e P` list pages | ⚠️ Returns True but no output | Use `win -dg` to count graphs |
| `echo %H` | ❌ Returns False | COM cannot capture LabTalk output |

## The golden workflow

1. Kill any existing Origin: `taskkill /f /im Origin64.exe`
2. `Dispatch("Origin.Application")` + `Visible = True`
3. Create workbook → fill data → set column types
4. Create graphs **one at a time**, formatting each immediately
5. Export each graph **individually** with `expGraph`
6. If `expGraph` returns True but no file, try `page.export(...)`
7. Never call `save` via COM — it crashes the connection

## Commands that work reliably

```labtalk
newproject
win -t wks
wks.ncols = 6
wks.nrows = 4
col(A)[1] = 10
col(B)[1] = 130.32
wks.col1.name$ = "Penetration(mm)"
wks.col1.type = 4                // set as X column
page.label$ = "Data"
win -a Data
plotxy iy:=(1,2) plot:=202 ogl:=[<new template:=Column>]
xb.text$ = "Penetration (mm)"
yl.text$ = "Cutting Force (N)"
layer.x.from = 0
layer.x.to = 65
layer.y.from = 0
layer.y.to = 700
label -s -sa -n title "(a) Combined Tool Forces"
```

## Export alternatives when expGraph fails

### Method 1: page.export (sometimes works)
```python
origin.Execute('page.export(type:=png, filename:=D:/path/to/fig.png)')
```

### Method 2: Screenshot via pyautogui
```python
import pyautogui
# Activate Origin window, then screenshot it
# (Origin HWND can be found via win32gui)
```

### Method 3: Clipboard copy from Origin
Origin's "Copy Graph as Image" can be triggered via Alt+E+C, then read from clipboard.

## Python boilerplate

```python
import win32com.client
import time
import pythoncom

pythoncom.CoInitialize()
try:
    origin = win32com.client.Dispatch("Origin.Application")
    origin.Visible = True
    time.sleep(3)  # Let Origin finish loading
    
    # ... send LabTalk commands via origin.Execute(cmd) ...
    
finally:
    pythoncom.CoUninitialize()
```

## cmd-style launch with script file

```
taskkill /f /im Origin64.exe
Start-Sleep 2
& "D:\Program Files\OriginLab\Origin2022\Origin64.exe" -rs "D:\path\to\script.ogs"
```

However, `expGraph` inside `.ogs` files still suffers from the same silent-failure bug.
Use COM + Python for export instead.

## Origin installation detection

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\OriginLab\Origin2022" -Name "Path" -ErrorAction SilentlyContinue
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\OriginLab\Origin2022" -Name "Path" -ErrorAction SilentlyContinue
# If neither found, search:
Get-ChildItem "C:\Program Files" -Recurse -Filter "Origin64.exe" -ErrorAction SilentlyContinue
Get-ChildItem "D:\Program Files" -Recurse -Filter "Origin64.exe" -ErrorAction SilentlyContinue
```
