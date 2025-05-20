#!/bin/bash

echo "📝 Création du fichier de configuration Tauri compatible avec la version 2.5.0..."

# Créer le nouveau fichier de configuration
cat > src-tauri/tauri.conf.json << 'EOF'
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/tooling/cli/schema.json",
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:5173",
    "distDir": "../dist",
    "withGlobalTauri": true
  },
  "package": {
    "productName": "Valetia",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": true,
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "copyFile": true,
        "createDir": true,
        "removeDir": true,
        "removeFile": true,
        "renameFile": true,
        "scope": ["**"]
      },
      "dialog": {
        "all": true,
        "open": true,
        "save": true
      },
      "path": {
        "all": true
      }
    },
    "bundle": {
      "active": true,
      "targets": ["appimage", "deb", "nsis"],
      "identifier": "com.valetia.app",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "category": "Productivity"
    },
    "security": {
      "csp": null
    },
    "updater": {
      "active": false
    },
    "windows": [
      {
        "fullscreen": false,
        "resizable": true,
        "title": "Valetia",
        "width": 1200,
        "height": 800
      }
    ]
  }
}
EOF

echo "✅ Configuration Tauri mise à jour!"
