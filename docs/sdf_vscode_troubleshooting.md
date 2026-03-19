# SDF Explorer Troubleshooting

## If pressing F5 does nothing

Most likely you opened the main project root instead of the extension folder.

This repo now supports both approaches:

### Option 1: Open the extension folder only

Open:

`vscode-sdf-explorer/`

Then press `F5`.

### Option 2: Open the main project root

Open:

`DocIntelligence/`

Then:

1. go to `Run and Debug`
2. choose `Run SDF Explorer Extension`
3. press `F5`

## If you still do not see anything happen

Check:

1. VS Code shows the `Run SDF Explorer Extension` launch configuration.
2. You have the built-in JavaScript debugger enabled.
3. You are not trying to run `extension.js` directly with Node.

## What should happen when it works

VS Code opens a second window called an Extension Development Host.

In that second window:

1. open an `.sdf` file
2. look for the `SDF` icon in the activity bar
3. use `SDF Explorer: Open SDF File` if needed
