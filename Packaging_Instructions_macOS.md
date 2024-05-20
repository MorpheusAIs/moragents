## Distribution

## Build and Sign
```sh
pyinstaller --windowed --runtime-hook runtime_hook.py --add-data "resources:resources" --osx-bundle-identifier "com.liquidtensor.moragents" --codesign-identity "Developer ID Application: Liquid Tensor LLC (ZQN244GMTD)" --name="MORagents" --icon="moragents.icns" --osx-entitlements-file "MORagents.entitlements" main.py
```

## Compress
```sh
ditto -c -k --sequesterRsrc --keepParent "MORagents.app" "MORagents.zip"
````

## Notarize
```sh
xcrun notarytool submit "MORagents.zip" --keychain-profile "NotaryProfile" --wait
```

## Staple App file
```shell
xcrun stapler staple "MORagents.app"
```

## Recreate zip archive post-stapling
```sh
ditto -c -k --sequesterRsrc --keepParent "MORagents.app" "MORagents.zip"
````

---


## Verify
```sh
codesign --verify --verbose=4 MORagents.app

codesign -dv --verbose=4 MORagents.app
```
