#!/bin/bash
set -e

echo "=== Hybrid Framework Auto Setup Script ==="

# 1. Install Homebrew
if ! command -v brew &> /dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew already installed"
fi

# 2. Python
brew install python
python3 --version

# 3. NodeJS
brew install node
node -v
npm -v

# 4. Appium
npm install -g appium
echo "Appium version: $(appium --version)"

# 5. Appium drivers
appium driver install xcuitest || true
appium driver install mac2 || true

# 6. Appium Doctor
npm install -g appium-doctor
appium-doctor --ios || true

# 7. Playwright dependencies
pip install -r requirements.txt
playwright install

# 8. Enable Safari driver
safaridriver --enable || true

# 9. Xcode tools
xcode-select --install || true
sudo xcodebuild -license accept || true

# 10. Finish
echo "=== SETUP COMPLETE ==="
