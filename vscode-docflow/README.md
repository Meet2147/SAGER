# DocFlow

Visualize and run `flow.dag.yaml` files from DocFlow directly inside VS Code.

## Features

- open a DocFlow YAML from the explorer context menu
- visualize nodes and dependencies in a webview
- run, debug, and step through a DocFlow
- inspect node config and dependency information
- supports files ending in `.flow.dag.yaml` and `.flow.dag.yml`

## Run in development

1. Open `vscode-docflow` in VS Code.
2. Press `F5`.
3. In the Extension Development Host, open a DocFlow file like:
   - `docflow/examples/document_preprocess.flow.dag.yaml`
4. Run:
   - `DocFlow: Visualize Active Flow`

## Commands

- `DocFlow: Visualize Flow File`
- `DocFlow: Visualize Active Flow`
