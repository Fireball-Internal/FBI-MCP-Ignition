# WhiskeyHouse VSCode Extension - Installation Guide

This guide describes how to install the `ignition-lint` WhiskeyHouse VSCode extension to enforce Spec-Driven Development (Perspective schema linting, Jython syntax checking) in your Ignition projects.

*Note: This guide explicitly excludes any `fast-mcp` integration, focusing solely on the VSCode extension functionality.*

## Prerequisites
- Visual Studio Code installed
- An Ignition project repository to lint

## Installation

You have two primary options for installing the WhiskeyHouse VSCode extension:

### Option 1: Install from VSCode Marketplace (Recommended)
If the extension is published to the VSCode Marketplace:
1. Open Visual Studio Code.
2. Go to the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`).
3. Search for **WhiskeyHouse** or **ignition-lint**.
4. Click **Install**.

### Option 2: Install from VSIX (Manual)
If you built the extension from source or were provided a `.vsix` file:
1. Open Visual Studio Code.
2. Go to the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X`).
3. Click the `...` (More Actions) menu in the top right of the Extensions view.
4. Select **Install from VSIX...**
5. Locate the downloaded `.vsix` file (e.g., in `c:\codebase\FBI-MCP-Ignition\ignition-lint\`) and install it.

## Usage & Configuration

Once installed, the extension will automatically begin linting relevant files in your opened workspace.

### Features Enabled by Default:
- **Perspective Component JSON Validation:** Automatically checks `view.json` files against empirical schemas to prevent malformed properties.
- **Jython Static Analysis:** Lints Jython scripts within your project for syntax errors and deprecated API usage.
- **Expression Binding Validation:** Validates expression structures.

*Ensure your VSCode workspace is rooted at your Ignition project directory for the best linting experience.*
