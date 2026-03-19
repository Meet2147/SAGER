let vscode;
try {
  vscode = require("vscode");
} catch (error) {
  if (require.main === module) {
    console.error(
      "This file is a VS Code extension entrypoint and cannot be run with plain Node.js.\n" +
      "Open the 'vscode-sdf-explorer' folder in VS Code and press F5 to launch the Extension Host."
    );
    process.exit(1);
  }
  throw error;
}

class SdfNode extends vscode.TreeItem {
  constructor(label, collapsibleState = vscode.TreeItemCollapsibleState.None, options = {}) {
    super(label, collapsibleState);
    this.kind = options.kind ?? "generic";
    this.payload = options.payload;
    this.children = options.children ?? null;
    this.description = options.description;
    this.tooltip = options.tooltip;
    this.contextValue = options.contextValue ?? this.kind;
    if (options.iconPath) {
      this.iconPath = options.iconPath;
    }
  }
}

class SdfTreeProvider {
  constructor() {
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    this.currentUri = null;
    this.document = null;
    this.rootNodes = [];
  }

  refresh() {
    this._onDidChangeTreeData.fire();
  }

  async openFile(uri) {
    let targetUri = uri;
    if (!targetUri) {
      const active = vscode.window.activeTextEditor?.document?.uri;
      if (active && active.fsPath.endsWith(".sdf")) {
        targetUri = active;
      } else {
        const selected = await vscode.window.showOpenDialog({
          canSelectMany: false,
          filters: { "SDF files": ["sdf"] },
          openLabel: "Open SDF file"
        });
        if (!selected || !selected.length) {
          return;
        }
        targetUri = selected[0];
      }
    }

    try {
      const bytes = await vscode.workspace.fs.readFile(targetUri);
      const text = Buffer.from(bytes).toString("utf8");
      this.document = JSON.parse(text);
      this.currentUri = targetUri;
      this.rootNodes = this.buildRootNodes(this.document, targetUri);
      this.refresh();
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to open SDF file: ${error.message}`);
    }
  }

  getTreeItem(element) {
    return element;
  }

  getChildren(element) {
    if (!this.currentUri || !this.document) {
      return [
        new SdfNode("No SDF file loaded", vscode.TreeItemCollapsibleState.None, {
          description: "Use 'Open SDF File' to load one"
        })
      ];
    }
    if (!element) {
      return this.rootNodes;
    }
    return element.children ?? [];
  }

  buildRootNodes(document, uri) {
    const atoms = Array.isArray(document.atoms) ? document.atoms : [];
    const edges = Array.isArray(document.edges) ? document.edges : [];
    const root = [
      this.objectNode("File", {
        path: uri.fsPath,
        format: document.format,
        version: document.version
      }, "file"),
      this.objectNode("Method", document.method ?? {}, "method"),
      this.objectNode("Source", document.source ?? {}, "source"),
      this.objectNode("Stats", document.stats ?? {}, "stats"),
      this.atomsNode(atoms),
      this.edgesNode(edges),
      this.objectNode("Annotations", document.annotations ?? {}, "annotations")
    ];
    return root;
  }

  objectNode(label, data, kind) {
    const entries = Object.entries(data ?? {}).map(([key, value]) =>
      new SdfNode(`${key}: ${this.formatValue(value)}`, vscode.TreeItemCollapsibleState.None, {
        kind: `${kind}-field`,
        tooltip: `${key}: ${JSON.stringify(value)}`
      })
    );
    return new SdfNode(label, entries.length ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.None, {
      kind,
      description: entries.length ? `${entries.length} fields` : "empty",
      children: entries
    });
  }

  atomsNode(atoms) {
    const pages = new Map();
    for (const atom of atoms) {
      const page = atom.page ?? 0;
      if (!pages.has(page)) {
        pages.set(page, []);
      }
      pages.get(page).push(atom);
    }

    const pageNodes = [...pages.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([page, pageAtoms]) => {
        const atomNodes = pageAtoms.slice(0, 200).map((atom) => this.atomNode(atom));
        const description = pageAtoms.length > 200 ? `${pageAtoms.length} atoms (showing 200)` : `${pageAtoms.length} atoms`;
        return new SdfNode(`Page ${page}`, vscode.TreeItemCollapsibleState.Collapsed, {
          kind: "page",
          description,
          children: atomNodes
        });
      });

    return new SdfNode("Atoms", vscode.TreeItemCollapsibleState.Expanded, {
      kind: "atoms",
      description: `${atoms.length} total`,
      children: pageNodes
    });
  }

  atomNode(atom) {
    const details = [
      ["atom_id", atom.atom_id],
      ["atom_type", atom.atom_type],
      ["role_label", atom.role_label],
      ["confidence", atom.confidence],
      ["reading_order", atom.reading_order],
      ["text", atom.text]
    ].filter(([, value]) => value !== undefined && value !== null);

    const childNodes = details.map(([key, value]) =>
      new SdfNode(`${key}: ${this.formatValue(value)}`, vscode.TreeItemCollapsibleState.None, {
        kind: "atom-field",
        tooltip: `${key}: ${typeof value === "string" ? value : JSON.stringify(value)}`
      })
    );

    return new SdfNode(atom.atom_id, vscode.TreeItemCollapsibleState.Collapsed, {
      kind: "atom",
      description: `p${atom.page} ${atom.role_label ?? atom.atom_type ?? ""}`.trim(),
      tooltip: atom.text,
      children: childNodes
    });
  }

  edgesNode(edges) {
    const grouped = new Map();
    for (const edge of edges) {
      const type = edge.edge_type ?? "unknown";
      if (!grouped.has(type)) {
        grouped.set(type, []);
      }
      grouped.get(type).push(edge);
    }

    const typeNodes = [...grouped.entries()]
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([type, typeEdges]) => {
        const edgeNodes = typeEdges.slice(0, 200).map((edge) => this.edgeNode(edge));
        const description = typeEdges.length > 200 ? `${typeEdges.length} edges (showing 200)` : `${typeEdges.length} edges`;
        return new SdfNode(type, vscode.TreeItemCollapsibleState.Collapsed, {
          kind: "edge-type",
          description,
          children: edgeNodes
        });
      });

    return new SdfNode("Edges", vscode.TreeItemCollapsibleState.Collapsed, {
      kind: "edges",
      description: `${edges.length} total`,
      children: typeNodes
    });
  }

  edgeNode(edge) {
    const childNodes = [
      ["source", edge.source],
      ["target", edge.target],
      ["weight", edge.weight]
    ].map(([key, value]) =>
      new SdfNode(`${key}: ${this.formatValue(value)}`, vscode.TreeItemCollapsibleState.None, {
        kind: "edge-field"
      })
    );

    return new SdfNode(`${edge.source} -> ${edge.target}`, vscode.TreeItemCollapsibleState.Collapsed, {
      kind: "edge",
      description: edge.edge_type,
      children: childNodes
    });
  }

  formatValue(value) {
    if (typeof value === "string") {
      return value.length > 100 ? `${value.slice(0, 97)}...` : value;
    }
    if (typeof value === "object") {
      return JSON.stringify(value);
    }
    return String(value);
  }
}

function activate(context) {
  const provider = new SdfTreeProvider();

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("sdfExplorer", provider),
    vscode.commands.registerCommand("sdfExplorer.openFile", async (uri) => {
      await provider.openFile(uri);
    }),
    vscode.commands.registerCommand("sdfExplorer.refresh", () => provider.refresh()),
    vscode.window.onDidChangeActiveTextEditor(async (editor) => {
      const uri = editor?.document?.uri;
      if (uri?.fsPath.endsWith(".sdf")) {
        await provider.openFile(uri);
      }
    })
  );
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
