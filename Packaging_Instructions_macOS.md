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

## Packaging/Distribution DIY Instructions

1. Download the latest [Packages App](http://s.sudre.free.fr/Software/Packages/about.html) [packages_1211_dev.dmg](http://s.sudre.free.fr/files/Packages_1211_dev.dmg)
2. Download the [MORAgentsInstallerFiles.zip](https://drive.google.com/drive/folders/16AEWPuzubAMS68kPU0DdNDZQL84EM1oA).
3. In the Packages App...
a) Create a New Project ... set the template as "Distribution".
b) Under the Packages, either edit the existing package or create a new one. Set "Identifier" to com.morpheus.pkg.MORAgents, set the Payload to have MORAgents.app under /Applications, then under Scripts, add the preinstall.sh and postinstall.sh from MORAgentsInstallerFiles.zip.
c) Create a new Package, then under Payload, add Docker.app from MORAgentsInstallerFiles.zip under /Applications
d) Navigate to Project, then set Presentation to have the welcome.html file and other settings to present the installer.
