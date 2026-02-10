## `README.md`

````markdown
# Hybrid Python Test Framework — Web + macOS + iPhone + iPad + API

This README helps you **set up everything from zero** on a clean macOS machine so your team can clone the repo → run commands → and start testing immediately.

---

# ✅ 1. Prerequisites
Framework requires:
- macOS
- Python **3.10+**
- Xcode (for iOS simulator)
- Homebrew
- NodeJS + Appium
- Playwright browsers

---

# ✅ 2. Install Homebrew (nếu chưa có)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
````

---

# ✅ 3. Install Python 3

```bash
brew install python
python3 --version
```

---

# ✅ 4. Create virtual environment

```bash
python3 -m venv .venv
source venv/bin/activate
```

---

# ✅ 5. Install project dependencies

```bash
pip install -r requirements.txt
```

---

# ✅ 6. Install Playwright browsers (Web testing)

```bash
playwright install
```

---

# ✅ 7. Install NodeJS (Appium dependency)

```bash
brew install node
node -v
npm -v
```

---

# ✅ 8. Install Appium

```bash
npm install -g appium
appium --version
```

---

# ✅ 9. Install Appium Drivers

## iOS Driver (XCUITest)

```bash
appium driver install xcuitest
```

## macOS Driver (mac2)

```bash
appium driver install mac2
```

---

# ✅ 10. Install Appium Doctor (check environment)

```bash
npm install -g appium-doctor
appium-doctor --ios
```

---

# ✅ 11. Install Xcode & CLI Tools (bắt buộc cho iPhone/iPad)

* Download Xcode from App Store
* Install CLI tools:

```bash
xcode-select --install
```

* Accept Xcode license:

```bash
sudo xcodebuild -license accept
```

---

# ✅ 12. Enable Safari automation (Web testing on Safari)

```bash
safaridriver --enable
```

---

# ✅ 13. Accessibility permissions (macOS App Testing)

macOS → System Settings → Privacy → Accessibility

* Add **Terminal**, **VSCode**, **PyCharm**, **Appium**
* Add the App under test if required

---

# ✅ 14. Configure capabilities

Edit JSON files:

```
resources/capabilities/ios_caps.json
resources/capabilities/mac_caps.json
```

Adjust:

* app path
* deviceName
* platformVersion

---

# ✅ 15. Start Appium server

```bash
appium
```

Or download Appium Inspector (GUI):
[https://github.com/appium/appium-inspector](https://github.com/appium/appium-inspector)

---

# 🚀 RUNNING TESTS

## Run all tests

```bash
pytest
```

## Run web tests

```bash
pytest -m web
```

## Run mobile tests (framework auto-selects iPhone/iPad via factory)

```bash
pytest tests/mobile/test_login_mobile.py
```

## Run macOS app tests

```bash
pytest -m mac
```

## Generate Allure Report

```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

# 🎯 Notes

* iOS requires proper signing if running on **real device**.
* Simulators require no signing.
* macOS automation depends on the OS accessibility API.
* Playwright does not require Selenium or Appium.
