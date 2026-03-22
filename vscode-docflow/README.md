# DocFlow for VS Code

DocFlow brings a PromptFlow-style visual editor to document processing pipelines inside VS Code.

It lets you open `*.flow.dag.yaml` and `*.flow.flex.yaml` files, inspect their node graph, edit flow inputs and outputs, run flows, debug them step by step, and export results to formats such as `json`, `txt`, `csv`, `xlsx`, and `sdf`.

## Demo

[![DocFlow visual editor](https://raw.githubusercontent.com/Meet2147/SAGER/main/vscode-docflow/media/docflow-editor.png)](https://raw.githubusercontent.com/Meet2147/SAGER/main/vscode-docflow/media/docflow-demo.mp4)

[Watch the demo video](https://raw.githubusercontent.com/Meet2147/SAGER/main/vscode-docflow/media/docflow-demo.mp4)

## What You Can Do

- Open DocFlow YAML files directly in a visual editor
- Create new flows with a built-in wizard
- Work with `standard`, `extraction`, `indexing`, `conversion`, and `evaluation` flow types
- Support both `dag` and `flex` orchestration styles
- Inspect inputs, outputs, node config, and dependencies
- Run flows from the editor with source/output settings
- Debug flows step by step from the designer toolbar
- Persist dragged node positions with layout sidecar files
- Export flow output to:
  - terminal
  - `json`
  - `txt`
  - `csv`
  - `xlsx`
  - `sdf`

## Supported Files

The extension recognizes:

- `.flow.dag.yaml`
- `.flow.dag.yml`
- `.flow.flex.yaml`
- `.flow.flex.yml`

## Commands

- `DocFlow: Create New Flow`
- `DocFlow: Open Visual Editor`
- `DocFlow: Open Visual Editor For Active Flow`

## Visual Editor Highlights

- PromptFlow-inspired three-pane layout
- YAML view on the left
- inputs, outputs, run settings, and node inspector in the middle
- vertical node graph designer on the right
- curved connectors with run-status coloring
- draggable nodes
- saved layout positions between sessions

## Create a New Flow

Use the command palette and run:

`DocFlow: Create New Flow`

The wizard lets you choose:

- Flow type:
  - `standard`
  - `extraction`
  - `indexing`
  - `conversion`
  - `evaluation`
- Orchestration:
  - `dag`
  - `flex`

## Run a Flow

1. Open a DocFlow YAML file.
2. Run `DocFlow: Open Visual Editor For Active Flow`.
3. Fill in:
   - source directory
   - output directory
   - output destination
   - export path if needed
4. Click the play button in the toolbar.

If a flow fails, errors are surfaced in:

- the DocFlow output channel
- the DocFlow terminal
- the visual node status panel

## Development

1. Open the `vscode-docflow` folder in VS Code.
2. Press `F5`.
3. In the Extension Development Host, open a sample flow such as:
   `docflow/examples/document_preprocess.flow.dag.yaml`
4. Run:
   `DocFlow: Open Visual Editor For Active Flow`

## Notes

- The extension is the visual/editor layer.
- The DocFlow Python library is the execution/runtime layer.
- Best results come from using the extension together with the `docflow-sager` package.
