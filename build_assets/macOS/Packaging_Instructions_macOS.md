## Distribution

## Build and Sign
```sh
pyinstaller --windowed --add-data "resources:resources" --osx-bundle-identifier "com.liquidtensor.moragents" --codesign-identity "Developer ID Application: Liquid Tensor LLC (ZQN244GMTD)" --name="MORagents" --icon="images/moragents.icns" --osx-entitlements-file "build_assets/macOS/MORagents.entitlements" main.py
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

### Verify notarization
```sh
xcrun notarytool info "<submission id>" --keychain-profile "NotaryProfile"  
```

```sh
codesign --verify --verbose=4 MORagents.app

codesign -dv --verbose=4 MORagents.app
```

## Wizard Creation

1. Download the dev version of the Packages app (it has to be the dev version because the latest build doesn't work on mac sonoma/last updated 2022) [Packages App](http://s.sudre.free.fr/Software/Packages/about.html) [packages_1211_dev.dmg](http://s.sudre.free.fr/files/Packages_1211_dev.dmg)
2. Download the files in https://github.com/MorpheusAIs/moragents/blob/a9d875b679df3e14e1d0a28704d00c001c99e340/build_assets/windows/, along with [Docker Desktop Mac Install](https://docs.docker.com/desktop/install/mac-install/) and MORAgents.app.
3. In the Packages App...\
a) Create a New Project ... set the template as "Distribution".\
b) Under the Packages, either edit the existing package or create a new one. Set "Identifier" to com.morpheus.pkg.MORAgents, set the Payload to have MORAgents.app under /Applications, then under Scripts, add the preinstall.sh and postinstall.sh from the downloaded files.\
c) Create a new Package, then under Payload, add the Docker Desktop Mac Install under /Applications\
d) Create a new Package, then under preinstall scripts, add the preinstall_ollama.sh script from the downloaded files.\
e) Navigate to Project, then set Presentation to have the welcome.html and license.html files and other settings to present the installer.

