## Distribution

For Mac:
```sh
$ pyinstaller --windowed --runtime-hook runtime_hook.py --add-data "resources:resources" --name="MORagents" --icon="moragents.icns" main.py
```

For Windows:
```shell
> pyinstaller --windowed --runtime-hook runtime_hook_windows.py --name="MORagents" --add-data "resources;resources" main.py
```



# Code signing
```sh
codesign --deep --force --verbose --sign "Developer ID Application: YourDeveloperName" MORagents.app
```

## Verify
```sh
codesign --verify --verbose=4 MORagents.app

codesign -dv --verbose=4 MORagents.app
```

---

# TODO
auto-install docker when "No such file or directory: '/usr/local/bin/docker'"
auto-remove containers
