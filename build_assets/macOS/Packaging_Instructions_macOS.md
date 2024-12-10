## Distribution

## Build and Sign MORagents.app
```sh
pyinstaller --windowed --osx-bundle-identifier "com.liquidtensor.moragents" --codesign-identity "Developer ID Application: Liquid Tensor LLC (ZQN244GMTD)" --name="MORagents" --icon="images/moragents.icns" --osx-entitlements-file "build_assets/macOS/MORagents.entitlements" main.py
```
NOTE: you will need to use your own codesigning identity if you intend to distribute. Codesigining is not required for running it on the same mac you built the .app on. For this you can drop the ```--codesign-identity "Developer ID Application: Liquid Tensor LLC (ZQN244GMTD)"``` part from the command.

## Wizard Creation
1. Install Packages app dev version [Packages App](http://s.sudre.free.fr/Software/Packages/about.html) [packages_1211_dev.dmg](http://s.sudre.free.fr/files/Packages_1211_dev.dmg)
3. $ mv dist/MORagents.app build_assets/macOS/
2. $ cd build_assets/macOS 
3. $ /usr/local/bin/packagesbuild --verbose --project MorpheusPackagesSudre.pkgproj

#1. Download the dev version of the Packages app (it has to be the dev version because the latest build doesn't work on mac sonoma/last updated 2022) [Packages App](http://s.sudre.free.fr/Software/Packages/about.html) [packages_1211_dev.dmg](http://s.sudre.free.fr/files/Packages_1211_dev.dmg)
#2. Download the files in https://github.com/MorpheusAIs/moragents/tree/main/build_assets/macOS, along with [Docker Desktop Mac Install](https://docs.docker.com/desktop/install/mac-install/) and the MORAgents.app you built in previous step.
#In the Packages App...\
#   1. Create a New Project ... set the template as "Distribution".\
#   2. Under the Packages, either edit the existing package or create a new one. Set "Identifier" to com.morpheus.pkg.MORAgents, set the Payload to have MORAgents.app under /Applications, then under Scripts, add the preinstall.sh and postinstall.sh from the downloaded files.\
#   3. Create a new Package, Set "Identifier" to com.morpheus.pkg.DockerDesktop, then under Payload, add the Docker Desktop Mac Install under /Applications\
#   4. Create a new Package, Set "Identifier" to com.morpheus.pkg.Ollama, then under preinstall scripts, add the preinstall_ollama.sh script from the downloaded files.\
#   5. Navigate to Project, then in Presentation click the topright dropdown and select Introduction choose the welcome.html file, add a License section and choose license.html.
#   6. In the upmost toolbar click Build -> Build to generate a .pkg file in the directory you saved the MORagents Packages package

---

>Note: Following steps are only required for distribution.
If you are just running the app on your own Mac you can run the .pkg you created, and then open MORagents from your searchbar.
Future usage only requires you to run MORagents from your searchbar.

---

## Signing
```sh
  productsign --sign "Developer ID Installer: Liquid Tensor LLC (ZQN244GMTD)" MORAgentsInstaller.pkg MORagents021-[apple\|intel].pkg
```

## Notarize
```sh
xcrun notarytool submit MORagents021-[apple\|intel].pkg --keychain-profile "NotaryProfile" --wait
```

## Staple
```sh
xcrun stapler staple MORagents021-[apple\|intel].pkg
```

---

## Verify (Optional)

### Verify notarization
```sh
xcrun notarytool info "<submission id>" --keychain-profile "NotaryProfile"
```

### Verify codesign
```sh
codesign --verify --verbose=4 MORagents.app

codesign -dv --verbose=4 MORagents.app
```
