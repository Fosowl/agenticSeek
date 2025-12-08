# Agent Guide

This document provides context and instructions for AI agents working on the Agentic Seek project.

## Project Overview
Agentic Seek is a hybrid application combining a React frontend with a Python-based backend logic, wrapped in a Capacitor shell for Android deployment.
- **Frontend**: React (TypeScript) located in `frontend/agentic-seek-front`.
- **Backend Logic**: Ported to TypeScript/Frontend for the Android app, or running as a separate service for other builds.
- **Android**: Capacitor project located in `frontend/agentic-seek-front/android`.

## Architecture & Key Components
*   **LLM Integration**: The app uses the Google Gemini API. The `LLMProvider` service handles requests and implements exponential backoff for `429` errors.
    *   *Note*: Defaults to `gemini-2.0-flash`.
*   **Browser Automation**: The Android port replaces Selenium/Playwright with `CapacitorHttp` for requests and `DOMParser` for scraping.
*   **State Management**: React state manages the UI, while backend logic handles the heavy lifting of search and parsing.

## Build Instructions

### Prerequisites
*   Node.js & npm
*   Android SDK (for Android builds) - Expected at `/usr/lib/android-sdk` or via `ANDROID_HOME`.

### Frontend Setup
Due to dependency conflicts (React Scripts vs TypeScript), you must use the legacy peer deps flag:
```bash
cd frontend/agentic-seek-front
npm install --legacy-peer-deps
```

### Android Build
To build the `.apk`:
1.  **Build Frontend**:
    ```bash
    npm run build
    ```
2.  **Sync Capacitor**:
    ```bash
    npx cap sync android
    ```
3.  **Compile APK**:
    ```bash
    cd android
    ./gradlew assembleDebug
    ```
    *   Artifact location: `android/app/build/outputs/apk/debug/app-debug.apk`

## Testing
*   **Frontend Tests**: Run `npm test` in `frontend/agentic-seek-front`.
    *   *Current Status*: Tests may fail due to Jest configuration issues with `react-markdown` ESM exports. Fixes are welcome but not blocking for builds.

## Release Process
*   **Versioning**: Update `package.json` and `android/app/build.gradle`.
*   **Artifacts**: Store the final APK in `releases/agentic-seek-android.apk`.

## Environment Variables
*   API Keys (e.g., Gemini) should be managed via environment variables or secure storage. DO NOT hardcode them.
