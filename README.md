## Distribution

```sh
$ pyinstaller --windowed --runtime-hook preinstall_hook.py --add-data "resources:resources" --name="MORagents" --icon="moragents.icns" main.py
```
