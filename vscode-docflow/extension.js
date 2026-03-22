let vscode;
try {
  vscode = require("vscode");
} catch (error) {
  if (require.main === module) {
    console.error(
      "This file is a VS Code extension entrypoint and cannot be run with plain Node.js.\n" +
      "Open the 'vscode-docflow' folder in VS Code and press F5 to launch the Extension Host."
    );
    process.exit(1);
  }
  throw error;
}
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

let docflowOutputChannel;
let docflowTerminal;

function activate(context) {
  docflowOutputChannel = vscode.window.createOutputChannel("DocFlow");
  context.subscriptions.push(
    docflowOutputChannel,
    vscode.commands.registerCommand("docflow.createFlow", async (uri) => {
      await createDocFlowWizard(uri);
    }),
    vscode.commands.registerCommand("docflow.visualizeFlow", async (uri) => {
      const target = await resolveFlowUri(uri);
      if (!target) {
        return;
      }
      await openFlowVisualizer(target);
    }),
    vscode.commands.registerCommand("docflow.visualizeActiveFlow", async () => {
      const target = await resolveFlowUri();
      if (!target) {
        return;
      }
      await openFlowVisualizer(target);
    })
  );
}

function deactivate() {}

async function createDocFlowWizard(uri) {
  const flowTypePick = await vscode.window.showQuickPick(
    [
      { label: "Standard", value: "standard", description: "General preprocessing and indexing flow" },
      { label: "Extraction", value: "extraction", description: "Extract structured outputs from documents" },
      { label: "Indexing", value: "indexing", description: "Prepare search and retrieval artifacts" },
      { label: "Conversion", value: "conversion", description: "Convert documents into downstream artifacts" },
      { label: "Evaluation", value: "evaluation", description: "Assess pipeline quality and coverage" }
    ],
    { placeHolder: "Choose the DocFlow type" }
  );
  if (!flowTypePick) {
    return;
  }

  const orchestrationPick = await vscode.window.showQuickPick(
    [
      { label: "DAG", value: "dag", description: "Node-based visual flow" },
      { label: "Flex", value: "flex", description: "Python-first flexible orchestration" }
    ],
    { placeHolder: "Choose the orchestration style" }
  );
  if (!orchestrationPick) {
    return;
  }

  const flowName = await vscode.window.showInputBox({
    prompt: "Flow name",
    value: `document_${flowTypePick.value}`,
    validateInput: (value) => value.trim() ? "" : "Flow name is required"
  });
  if (!flowName) {
    return;
  }

  const targetFolder = await resolveCreateFlowFolder(uri);
  if (!targetFolder) {
    return;
  }

  const safeName = flowName.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "docflow";
  const fileName = `${safeName}.flow.${orchestrationPick.value}.yaml`;
  const targetUri = vscode.Uri.joinPath(targetFolder, fileName);
  const template = buildFlowTemplate({
    flowName: safeName,
    flowType: flowTypePick.value,
    orchestration: orchestrationPick.value
  });

  await vscode.workspace.fs.writeFile(targetUri, Buffer.from(template, "utf8"));
  const document = await vscode.workspace.openTextDocument(targetUri);
  await vscode.window.showTextDocument(document);
  vscode.window.showInformationMessage(`Created ${fileName}`);
}

async function resolveCreateFlowFolder(uri) {
  if (uri?.scheme === "file") {
    try {
      const stat = await vscode.workspace.fs.stat(uri);
      if (stat.type & vscode.FileType.Directory) {
        return uri;
      }
      return vscode.Uri.file(path.dirname(uri.fsPath));
    } catch (error) {
      // fall through to workspace/default selection
    }
  }

  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  const defaultUri = workspaceFolder?.uri;
  const selected = await vscode.window.showOpenDialog({
    canSelectMany: false,
    canSelectFiles: false,
    canSelectFolders: true,
    defaultUri,
    openLabel: "Create flow here"
  });
  return selected?.[0] || defaultUri || null;
}

function buildFlowTemplate({ flowName, flowType, orchestration }) {
  const datasetName = `${flowType}_demo`;
  const outputDir = `docflow_runs/${flowType}`;
  const extension = orchestration === "flex" ? "flow.flex.yaml" : "flow.dag.yaml";
  const maybeOrchestrationLine = orchestration === "flex" ? "orchestration: flex\n" : "";
  const nodes = templateNodesForFlowType(flowType);
  return `name: ${flowName}
flow_type: ${flowType}
${maybeOrchestrationLine}variables:
  dataset_name: ${datasetName}
  output_dir: ${outputDir}

nodes:
${nodes}
outputs:
  final_node: write
`;
}

function templateNodesForFlowType(flowType) {
  const scan = `  - name: scan
    step: scan_documents
    config:
      source_dir: \${inputs.source_dir}
      file_types: [pdf, docx, doc, xlsx, xls, msg]
`;
  const parse = `  - name: parse
    step: parse_documents
    depends_on: [scan]
    config:
      dataset_name: \${dataset_name}
`;
  const normalize = `  - name: normalize
    step: normalize_atoms
    depends_on: [parse]
`;
  const metadata = `  - name: metadata
    step: enrich_metadata
    depends_on: [normalize]
`;
  const graph = `  - name: graph
    step: build_evidence_graph
    depends_on: [metadata]
`;
  const indexes = `  - name: indexes
    step: build_indexes
    depends_on: [graph]
`;
  const writeFromMetadata = `  - name: write
    step: write_outputs
    depends_on: [metadata]
    config:
      output_dir: \${output_dir}
`;
  const writeFromGraph = `  - name: write
    step: write_outputs
    depends_on: [graph]
    config:
      output_dir: \${output_dir}
`;
  const writeFromIndexes = `  - name: write
    step: write_outputs
    depends_on: [graph, indexes]
    config:
      output_dir: \${output_dir}
`;

  if (flowType === "conversion") {
    return `${scan}${parse}${normalize}${metadata}${writeFromMetadata}`;
  }
  if (flowType === "extraction") {
    return `${scan}${parse}${normalize}${metadata}${graph}${writeFromGraph}`;
  }
  return `${scan}${parse}${normalize}${metadata}${graph}${indexes}${writeFromIndexes}`;
}

async function resolveFlowUri(uri) {
  if (uri && isDocFlowFile(uri)) {
    return uri;
  }

  const active = vscode.window.activeTextEditor?.document?.uri;
  if (active && isDocFlowFile(active)) {
    return active;
  }

  const selected = await vscode.window.showOpenDialog({
    canSelectMany: false,
    filters: { "DocFlow files": ["yaml", "yml"] },
    openLabel: "Open flow.dag.yaml"
  });
  if (!selected || !selected.length) {
    return null;
  }
  return selected[0];
}

function isDocFlowFile(uri) {
  const targetPath = uri.fsPath.toLowerCase();
  return (
    targetPath.endsWith(".flow.dag.yaml") ||
    targetPath.endsWith(".flow.dag.yml") ||
    targetPath.endsWith(".flow.flex.yaml") ||
    targetPath.endsWith(".flow.flex.yml")
  );
}

async function openFlowVisualizer(uri) {
  try {
    const bytes = await vscode.workspace.fs.readFile(uri);
    const text = Buffer.from(bytes).toString("utf8");
    const graph = parseDocFlow(text, uri.fsPath);
    graph.layout = await loadFlowLayout(uri);

    const panel = vscode.window.createWebviewPanel(
      "docflowVisualizer",
      `DocFlow: ${graph.flowName}`,
      vscode.ViewColumn.Beside,
      { enableScripts: true, retainContextWhenHidden: true }
    );
    panel.webview.html = buildHtml(graph);
    panel.webview.onDidReceiveMessage(async (message) => {
      if (message.type === "play") {
        await executeDocFlow(uri, graph, panel, message.payload || {});
      } else if (message.type === "saveLayout") {
        await saveFlowLayout(uri, message.payload || {});
      }
    });
  } catch (error) {
    vscode.window.showErrorMessage(`Failed to visualize DocFlow file: ${error.message}`);
  }
}

async function loadFlowLayout(flowUri) {
  const layoutUri = getFlowLayoutUri(flowUri);
  try {
    const bytes = await vscode.workspace.fs.readFile(layoutUri);
    const parsed = JSON.parse(Buffer.from(bytes).toString("utf8"));
    return {
      version: parsed.version || "1",
      flowName: parsed.flowName || path.basename(flowUri.fsPath),
      positions: parsed.positions && typeof parsed.positions === "object" ? parsed.positions : {}
    };
  } catch (error) {
    return {
      version: "1",
      flowName: path.basename(flowUri.fsPath),
      positions: {}
    };
  }
}

async function saveFlowLayout(flowUri, payload) {
  const layoutUri = getFlowLayoutUri(flowUri);
  const parentUri = vscode.Uri.file(path.dirname(layoutUri.fsPath));
  const safePayload = {
    version: "1",
    flowName: payload.flowName || path.basename(flowUri.fsPath),
    updatedAt: new Date().toISOString(),
    positions: payload.positions && typeof payload.positions === "object" ? payload.positions : {}
  };
  await vscode.workspace.fs.createDirectory(parentUri);
  await vscode.workspace.fs.writeFile(layoutUri, Buffer.from(JSON.stringify(safePayload, null, 2), "utf8"));
}

function getFlowLayoutUri(flowUri) {
  const fileName = path.basename(flowUri.fsPath).replace(/\.(ya?ml)$/i, ".layout.json");
  return vscode.Uri.joinPath(vscode.Uri.file(path.dirname(flowUri.fsPath)), ".docflow", fileName);
}

async function executeDocFlow(flowUri, graph, panel, options) {
  const projectRoot = findProjectRoot(flowUri.fsPath);
  if (!projectRoot) {
    vscode.window.showErrorMessage("Could not locate the DocFlow project root for this flow.");
    return;
  }

  const defaultSource = path.join(projectRoot, "data", "Books");
  const sourceDir = options.sourceDir || await vscode.window.showInputBox({
    prompt: "Source directory for DocFlow run",
    value: defaultSource
  });
  if (!sourceDir) {
    return;
  }

  const defaultOutput = path.join(projectRoot, "docflow_runs", graph.flowName);
  const outputDir = options.outputDir || await vscode.window.showInputBox({
    prompt: "Output directory for DocFlow run",
    value: defaultOutput
  });
  if (!outputDir) {
    return;
  }

  const exportFormat = options.exportFormat || "terminal";
  let exportPath = options.exportPath || "";
  if (exportFormat !== "terminal" && !exportPath) {
    exportPath = await vscode.window.showInputBox({
      prompt: `Export path for ${exportFormat.toUpperCase()} output`,
      value: path.join(outputDir, `docflow_output.${exportFormat}`)
    }) || "";
  }

  panel.webview.postMessage({ type: "runStarted", sourceDir, outputDir });

  const scriptPath = path.join(projectRoot, "scripts", "run_docflow.py");
  const args = [scriptPath, flowUri.fsPath, "--source-dir", sourceDir, "--output-dir", outputDir, "--trace", "--export-format", exportFormat];
  if (exportFormat !== "terminal" && exportPath) {
    args.push("--export-path", exportPath);
  }
  const commandLine = ["python3", ...args].join(" ");
  appendRunHeader(commandLine);
  const child = spawn("python3", args, { cwd: projectRoot });

  let stdout = "";
  let stderr = "";
  child.stdout.on("data", (chunk) => {
    const text = chunk.toString();
    stdout += text;
    docflowOutputChannel.append(text);
  });
  child.stderr.on("data", (chunk) => {
    const text = chunk.toString();
    stderr += text;
    docflowOutputChannel.append(text);
  });

  child.on("close", (code) => {
    if (code !== 0) {
      revealFailure(stderr || stdout || `DocFlow exited with code ${code}`);
      panel.webview.postMessage({
        type: "runError",
        message: stderr || stdout || `DocFlow exited with code ${code}`
      });
      return;
    }
    try {
      const payload = JSON.parse(stdout);
      panel.webview.postMessage({
        type: "runCompleted",
        payload
      });
    } catch (error) {
      panel.webview.postMessage({
        type: "runError",
        message: `Failed to parse DocFlow output: ${error.message}`
      });
    }
  });
}

function findProjectRoot(startFile) {
  let current = path.dirname(startFile);
  while (true) {
    const candidate = path.join(current, "scripts", "run_docflow.py");
    if (fs.existsSync(candidate)) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      return null;
    }
    current = parent;
  }
}

function appendRunHeader(commandLine) {
  docflowOutputChannel.clear();
  docflowOutputChannel.appendLine("=== DocFlow Run ===");
  docflowOutputChannel.appendLine(commandLine);
  docflowOutputChannel.appendLine("");
  docflowOutputChannel.show(true);
}

function revealFailure(message) {
  docflowOutputChannel.appendLine("");
  docflowOutputChannel.appendLine("=== DocFlow Failure ===");
  docflowOutputChannel.appendLine(message);
  docflowOutputChannel.show(true);

  const terminal = getDocflowTerminal();
  terminal.show(true);
  terminal.sendText(buildTerminalEcho(message), true);
}

function getDocflowTerminal() {
  if (!docflowTerminal || docflowTerminal.exitStatus) {
    docflowTerminal = vscode.window.createTerminal("DocFlow Errors");
  }
  return docflowTerminal;
}

function buildTerminalEcho(message) {
  const marker = "DOCFLOW_ERROR_BLOCK";
  return `cat <<'${marker}'\n${message}\n${marker}`;
}

function parseDocFlow(text, filePath) {
  const lines = text.replace(/\t/g, "  ").split(/\r?\n/);
  let flowName = "docflow";
  let flowType = "standard";
  let orchestration = inferOrchestrationFromPath(filePath);
  let finalNode = null;
  const nodes = [];
  const flowInputs = [];
  const flowOutputs = [];
  let inNodes = false;
  let current = null;
  let currentSection = null;
  let section = null;
  let currentField = null;

  for (const rawLine of lines) {
    const indent = rawLine.match(/^ */)[0].length;
    const trimmed = rawLine.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    if (trimmed.startsWith("name:")) {
      flowName = trimmed.slice(5).trim();
      continue;
    }
    if (trimmed.startsWith("flow_type:")) {
      flowType = trimmed.slice("flow_type:".length).trim() || "standard";
      continue;
    }
    if (trimmed.startsWith("orchestration:")) {
      orchestration = trimmed.slice("orchestration:".length).trim() || orchestration;
      continue;
    }
    if (trimmed === "inputs:") {
      section = "inputs";
      inNodes = false;
      current = null;
      currentField = null;
      continue;
    }
    if (trimmed === "outputs:") {
      section = "outputs";
      inNodes = false;
      current = null;
      currentField = null;
      continue;
    }
    if (trimmed === "nodes:") {
      inNodes = true;
      section = "nodes";
      current = null;
      currentSection = null;
      currentField = null;
      continue;
    }
    if (!inNodes && section === "outputs" && trimmed.startsWith("final_node:")) {
      finalNode = trimmed.slice("final_node:".length).trim();
      continue;
    }
    if (!inNodes && (section === "inputs" || section === "outputs")) {
      const collection = section === "inputs" ? flowInputs : flowOutputs;
      if (indent === 2 && /^[A-Za-z0-9_]+:/.test(trimmed)) {
        const idx = trimmed.indexOf(":");
        currentField = {
          name: trimmed.slice(0, idx).trim(),
          type: "",
          value: "",
          reference: "",
          details: {}
        };
        collection.push(currentField);
        continue;
      }
      if (currentField && indent >= 4 && /^[A-Za-z0-9_]+:/.test(trimmed)) {
        const idx = trimmed.indexOf(":");
        const key = trimmed.slice(0, idx).trim();
        const value = trimmed.slice(idx + 1).trim();
        currentField.details[key] = parseScalar(value);
        if (key === "type") {
          currentField.type = value;
        } else if (key === "default") {
          currentField.value = value;
        } else if (key === "reference") {
          currentField.reference = value;
        }
        continue;
      }
    }
    if (!inNodes) {
      continue;
    }

    if (trimmed.startsWith("- name:")) {
      current = {
        id: trimmed.slice("- name:".length).trim(),
        step: "",
        depends_on: [],
        config: {}
      };
      nodes.push(current);
      currentSection = null;
      continue;
    }

    if (!current) {
      continue;
    }

    if (trimmed.startsWith("step:")) {
      current.step = trimmed.slice(5).trim();
      continue;
    }
    if (trimmed.startsWith("depends_on:")) {
      current.depends_on = parseInlineList(trimmed.slice("depends_on:".length).trim());
      continue;
    }
    if (trimmed === "config:") {
      currentSection = "config";
      continue;
    }
    if (currentSection === "config" && /^[A-Za-z0-9_]+:/.test(trimmed)) {
      const idx = trimmed.indexOf(":");
      const key = trimmed.slice(0, idx).trim();
      const value = trimmed.slice(idx + 1).trim();
      current.config[key] = parseScalar(value);
    }
  }

  const depths = computeDepths(nodes);
  return {
    flowName,
    flowType,
    orchestration,
    filePath,
    fileName: path.basename(filePath || "flow.dag.yaml"),
    finalNode,
    inputs: flowInputs,
    outputs: flowOutputs,
    nodes: nodes.map((node) => ({
      ...node,
      depth: depths.get(node.id) ?? 0
    })),
    edges: nodes.flatMap((node) => node.depends_on.map((dependency) => ({ source: dependency, target: node.id })))
  };
}

function inferOrchestrationFromPath(filePath) {
  const lowered = String(filePath || "").toLowerCase();
  return lowered.includes(".flex.") ? "flex" : "dag";
}

function parseInlineList(value) {
  const cleaned = value.trim();
  if (!cleaned.startsWith("[") || !cleaned.endsWith("]")) {
    return cleaned ? [cleaned] : [];
  }
  const inner = cleaned.slice(1, -1).trim();
  if (!inner) {
    return [];
  }
  return inner.split(",").map((item) => item.trim()).filter(Boolean);
}

function parseScalar(value) {
  if (!value) {
    return "";
  }
  if (value.startsWith("[") && value.endsWith("]")) {
    return parseInlineList(value);
  }
  return value;
}

function computeDepths(nodes) {
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const memo = new Map();

  function resolve(id) {
    if (memo.has(id)) {
      return memo.get(id);
    }
    const node = nodeMap.get(id);
    if (!node || !node.depends_on.length) {
      memo.set(id, 0);
      return 0;
    }
    const depth = Math.max(...node.depends_on.map(resolve)) + 1;
    memo.set(id, depth);
    return depth;
  }

  for (const node of nodes) {
    resolve(node.id);
  }
  return memo;
}

function buildHtml(graph) {
  const payload = JSON.stringify(graph);
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(graph.flowName)}</title>
  <style>
    :root {
      --bg: #1e1e1e;
      --panel: #252526;
      --panel-2: #2d2d30;
      --panel-3: #1f1f1f;
      --border: #3c3c3c;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #0e639c;
      --accent-2: #3794ff;
      --success: #16a34a;
      --shadow: rgba(0,0,0,0.28);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
    }
    .page {
      height: 100vh;
      display: grid;
      grid-template-columns: 32% 30% 38%;
    }
    .pane {
      min-width: 0;
      min-height: 0;
      border-right: 1px solid var(--border);
      background: var(--panel);
    }
    .pane:last-child {
      border-right: 0;
      background: var(--panel-3);
    }
    .pane-header {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: var(--panel);
    }
    .pane-header h1, .pane-header h2 {
      margin: 0;
      font-size: 13px;
      font-weight: 600;
    }
    .subtle {
      color: var(--muted);
      font-size: 11px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .editor-pane {
      display: grid;
      grid-template-rows: auto 1fr;
      background: #1e1e1e;
    }
    .editor-tabs {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px 0;
      border-bottom: 1px solid var(--border);
      background: #252526;
    }
    .tab {
      padding: 8px 12px;
      border: 1px solid var(--border);
      border-bottom: 0;
      border-top-left-radius: 6px;
      border-top-right-radius: 6px;
      background: #2d2d30;
      font-size: 12px;
    }
    .editor-body {
      overflow: auto;
      padding: 14px 18px 28px;
      font-family: Consolas, "Courier New", monospace;
      font-size: 12px;
      line-height: 1.8;
      color: #d4d4d4;
    }
    .code-line {
      display: grid;
      grid-template-columns: 34px 1fr;
      gap: 12px;
      white-space: pre-wrap;
    }
    .line-no {
      text-align: right;
      color: #6b7280;
      user-select: none;
    }
    .line-text .key { color: #4fc1ff; }
    .line-text .value { color: #ce9178; }
    .line-text .name { color: #dcdcaa; }
    .line-text .ref { color: #c586c0; }
    .middle-pane {
      display: grid;
      grid-template-rows: auto auto 1fr;
      min-height: 0;
    }
    .block {
      margin: 12px;
      border: 1px solid var(--border);
      background: var(--panel-2);
    }
    .block-header {
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      font-size: 13px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
    }
    .block-title {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .collapse-icon {
      color: var(--muted);
      font-size: 12px;
      width: 10px;
      display: inline-flex;
      justify-content: center;
      transition: transform 120ms ease;
    }
    .block.collapsed .block-body {
      display: none;
    }
    .block.collapsed .collapse-icon {
      transform: rotate(-90deg);
    }
    .block-body {
      padding: 8px 12px 12px;
    }
    .add-row-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      height: 28px;
      padding: 0 10px;
      border-radius: 4px;
      border: 1px solid #ea580c;
      background: #c2410c;
      color: white;
      font-size: 12px;
      cursor: pointer;
      margin-top: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      padding: 8px 6px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }
    th { color: var(--muted); font-weight: 600; }
    tr:last-child td { border-bottom: 0; }
    input[type="text"], select {
      width: 100%;
      height: 30px;
      background: #1f1f1f;
      color: var(--text);
      border: 1px solid #ea580c;
      padding: 0 8px;
      font-size: 12px;
      outline: none;
    }
    input[type="checkbox"], input[type="radio"] {
      accent-color: #ea580c;
    }
    .exec-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }
    .field {
      display: grid;
      gap: 6px;
    }
    .field label {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .node-inspector {
      margin: 0 12px 12px;
      border: 1px solid var(--border);
      background: var(--panel-2);
      overflow: auto;
      min-height: 0;
    }
    .node-inspector-header {
      padding: 12px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .node-inspector-title {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .node-inspector-title strong { font-size: 13px; }
    .tag {
      display: inline-flex;
      align-items: center;
      height: 22px;
      padding: 0 8px;
      border-radius: 999px;
      background: rgba(14,99,156,0.22);
      color: #8ed0ff;
      border: 1px solid rgba(55,148,255,0.35);
      font-size: 11px;
      font-weight: 700;
    }
    .inspector-section {
      padding: 12px;
      border-bottom: 1px solid var(--border);
    }
    .inspector-section:last-child { border-bottom: 0; }
    .inspector-label {
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    pre {
      margin: 0;
      padding: 10px;
      background: #1b1b1b;
      border: 1px solid var(--border);
      overflow: auto;
      color: #d4d4d4;
      font-family: Consolas, "Courier New", monospace;
      font-size: 12px;
    }
    .designer-pane {
      display: grid;
      grid-template-rows: auto 1fr;
      min-height: 0;
    }
    .designer-toolbar {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: var(--panel);
    }
    .designer-left {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }
    .env-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: #d1d5db;
      font-size: 12px;
      white-space: nowrap;
    }
    .designer-meta {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 12px;
    }
    .designer-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-left: 12px;
    }
    .action-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 24px;
      min-width: 24px;
      padding: 0 6px;
      border-radius: 4px;
      border: 1px solid #4b5563;
      background: transparent;
      color: #d1d5db;
      font-size: 11px;
      cursor: pointer;
    }
    .action-btn:hover {
      background: #2d2d30;
      border-color: #6b7280;
    }
    .action-btn.primary {
      color: #e5e7eb;
    }
    .action-btn.secondary {
      color: #d1d5db;
    }
    .action-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .run-status {
      color: var(--muted);
      font-size: 12px;
      min-width: 120px;
    }
    .designer-canvas-wrap {
      overflow: auto;
      padding: 18px;
    }
    #canvas {
      position: relative;
      min-height: 100%;
      background: #1e1e1e;
    }
    #edges {
      position: absolute;
      inset: 0;
      overflow: visible;
      pointer-events: none;
    }
    .endpoint {
      position: absolute;
      width: 82px;
      height: 34px;
      border-radius: 12px;
      border: 2px solid #6b7280;
      background: #1e1e1e;
      color: #f9fafb;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
    }
    .node {
      position: absolute;
      width: 204px;
      min-height: 74px;
      border-radius: 6px;
      border: 1px solid #4b5563;
      background: #1f1f1f;
      box-shadow: 0 10px 22px var(--shadow);
      overflow: hidden;
      cursor: pointer;
      text-align: left;
      user-select: none;
    }
    .node.dragging {
      cursor: grabbing;
      box-shadow: 0 12px 26px rgba(0,0,0,0.34);
    }
    .node.active {
      border-color: var(--accent-2);
      box-shadow: 0 0 0 1px var(--accent-2);
    }
    .node.final {
      border-color: var(--success);
    }
    .node.status-running {
      border-color: rgba(245, 158, 11, 0.85);
      box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.35);
    }
    .node.status-completed {
      border-color: rgba(34, 197, 94, 0.72);
      box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.24);
    }
    .node.status-error {
      border-color: rgba(239, 68, 68, 0.75);
      box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.22);
    }
    .node.status-idle .node-topbar { background: #4b5563; }
    .node.status-running .node-topbar { background: #eab308; }
    .node.status-completed .node-topbar { background: var(--success); }
    .node.status-error .node-topbar { background: #ef4444; }
    .node-topbar {
      height: 4px;
      background: #3b82f6;
    }
    .node-body {
      padding: 10px 12px 10px;
    }
    .node-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      font-size: 13px;
      font-weight: 700;
      color: #f3f4f6;
    }
    .node-icon {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: #60a5fa;
      flex: 0 0 auto;
    }
    .node-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      color: #86efac;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--success);
      flex: 0 0 auto;
    }
    .node.status-idle .status-dot { background: #6b7280; }
    .node.status-running .status-dot { background: #eab308; }
    .node.status-completed .status-dot { background: var(--success); }
    .node.status-error .status-dot { background: #ef4444; }
    .edge-path {
      stroke: #8b8b8b;
      stroke-width: 1.8;
      fill: none;
      stroke-linecap: round;
      transition: stroke 160ms ease, stroke-width 160ms ease, opacity 160ms ease;
      opacity: 0.92;
    }
    .edge-path.edge-idle { stroke: #8b8b8b; }
    .edge-path.edge-running {
      stroke: #a78bfa;
      stroke-width: 2.2;
      stroke-dasharray: 7 7;
      animation: edgeFlow 0.9s linear infinite;
    }
    .edge-path.edge-completed { stroke: #9ca3af; }
    .edge-path.edge-success { stroke: #22c55e; stroke-width: 2.1; }
    .edge-path.edge-error { stroke: #ef4444; stroke-width: 2.1; }
    .edge-arrow {
      transition: fill 160ms ease, opacity 160ms ease;
      opacity: 0.95;
    }
    .edge-arrow.edge-idle { fill: #8b8b8b; }
    .edge-arrow.edge-running { fill: #a78bfa; }
    .edge-arrow.edge-completed { fill: #9ca3af; }
    .edge-arrow.edge-success { fill: #22c55e; }
    .edge-arrow.edge-error { fill: #ef4444; }
    @keyframes edgeFlow {
      from { stroke-dashoffset: 14; }
      to { stroke-dashoffset: 0; }
    }
    @media (max-width: 1280px) {
      .page { grid-template-columns: 1fr; }
      .pane { border-right: 0; border-bottom: 1px solid var(--border); }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="pane editor-pane">
      <div class="editor-tabs">
        <div class="tab">${escapeHtml(graph.fileName || "flow.dag.yaml")}</div>
        <div class="subtle">YAML</div>
        <div class="subtle">Visual editor</div>
      </div>
      <div class="editor-body" id="yaml-outline"></div>
    </section>
    <section class="pane middle-pane">
      <div class="pane-header">
        <div>
          <h2>Visual editor</h2>
          <div class="subtle">${escapeHtml(graph.flowName)} · ${escapeHtml(graph.flowType)} · ${escapeHtml(graph.orchestration)}</div>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
          <div class="tag">${escapeHtml(graph.flowType)}</div>
          <div class="tag">${escapeHtml(graph.orchestration)}</div>
          <div class="tag">${escapeHtml(graph.inputs.length + " inputs")}</div>
        </div>
      </div>
      <div class="block">
        <div class="block-header"><span class="block-title"><span class="collapse-icon">▾</span><span>Inputs</span></span><span class="subtle" id="input-count"></span></div>
        <div class="block-body">
          <table>
            <thead><tr><th>Name</th><th>Type</th><th>Default value</th></tr></thead>
            <tbody id="inputs-table"></tbody>
          </table>
          <button class="add-row-btn" id="add-input-btn">+ Add input</button>
        </div>
      </div>
      <div class="block">
        <div class="block-header"><span class="block-title"><span class="collapse-icon">▾</span><span>Outputs</span></span><span class="subtle" id="output-count"></span></div>
        <div class="block-body">
          <table>
            <thead><tr><th>Name</th><th>Reference</th></tr></thead>
            <tbody id="outputs-table"></tbody>
          </table>
          <button class="add-row-btn" id="add-output-btn">+ Add output</button>
        </div>
      </div>
      <div class="block">
        <div class="block-header"><span class="block-title"><span class="collapse-icon">▾</span><span>Run settings</span></span><span class="subtle">terminal or file</span></div>
        <div class="block-body">
          <div class="exec-grid">
            <div class="field">
              <label for="source-dir-input">Source directory</label>
              <input type="text" id="source-dir-input" placeholder="/path/to/documents" />
            </div>
            <div class="field">
              <label for="output-dir-input">Output directory</label>
              <input type="text" id="output-dir-input" placeholder="/path/to/output" />
            </div>
            <div class="field">
              <label for="export-format-input">Output destination</label>
              <select id="export-format-input">
                <option value="terminal">Terminal</option>
                <option value="json">JSON file</option>
                <option value="txt">TXT file</option>
                <option value="csv">CSV file</option>
                <option value="xlsx">XLSX file</option>
                <option value="sdf">SDF file</option>
              </select>
            </div>
            <div class="field">
              <label for="export-path-input">Export file path</label>
              <input type="text" id="export-path-input" placeholder="/path/to/output.json" />
            </div>
          </div>
        </div>
      </div>
      <div class="node-inspector">
        <div class="node-inspector-header">
          <div class="node-inspector-title">
            <strong id="selected-name">Click a node</strong>
            <span id="selected-step">No node selected</span>
          </div>
          <span class="tag" id="selected-status">Node</span>
        </div>
        <div class="inspector-section">
          <div class="inspector-label">Depends On</div>
          <div id="selected-deps">No node selected</div>
        </div>
        <div class="inspector-section">
          <div class="inspector-label">Config</div>
          <pre id="selected-config">{}</pre>
        </div>
      </div>
    </section>
    <section class="pane designer-pane">
      <div class="designer-toolbar">
        <div class="designer-left">
          <div class="env-badge">⚙ Python env: /usr/local/bin/python3</div>
        </div>
        <div class="designer-meta">
          <span id="graph-summary"></span>
          <span>type: <strong id="flow-type"></strong></span>
          <span>mode: <strong id="flow-orchestration"></strong></span>
          <span>final: <strong id="final-node"></strong></span>
          <div class="designer-actions">
            <button class="action-btn primary" id="run-flow-btn" title="Run flow">▶</button>
            <button class="action-btn secondary" id="debug-flow-btn" title="Debug flow">⚗</button>
            <button class="action-btn secondary" id="step-debug-btn" title="Step debug" disabled>↷</button>
          </div>
          <span class="run-status" id="run-status">Idle</span>
        </div>
      </div>
      <div class="designer-canvas-wrap">
        <div id="canvas">
          <svg id="edges"></svg>
          <div class="endpoint" id="inputs-node">inputs</div>
          <div class="endpoint" id="outputs-node">outputs</div>
        </div>
      </div>
    </section>
  </div>
  <script>
    const vscodeApi = acquireVsCodeApi();
    const graph = ${payload};
    const canvas = document.getElementById("canvas");
    const edgesSvg = document.getElementById("edges");
    const columnWidth = 248;
    const rowHeight = 132;
    const cardWidth = 204;
    const cardHeight = 78;
    const marginX = 72;
    const marginY = 90;
    const inputsNode = document.getElementById("inputs-node");
    const outputsNode = document.getElementById("outputs-node");
    const runStatusEl = document.getElementById("run-status");
    const runButton = document.getElementById("run-flow-btn");
    const debugButton = document.getElementById("debug-flow-btn");
    const stepButton = document.getElementById("step-debug-btn");
    const addInputButton = document.getElementById("add-input-btn");
    const addOutputButton = document.getElementById("add-output-btn");
    const sourceDirInput = document.getElementById("source-dir-input");
    const outputDirInput = document.getElementById("output-dir-input");
    const exportFormatInput = document.getElementById("export-format-input");
    const exportPathInput = document.getElementById("export-path-input");
    const nodeElements = new Map();
    const nodeStatuses = new Map(graph.nodes.map((node) => [node.id, "idle"]));
    const edgeElements = [];
    let dragState = null;
    let layoutSaveTimer = null;
    const flowInputs = (graph.inputs || []).map((item) => ({ ...item }));
    const flowOutputs = (graph.outputs || []).map((item) => ({ ...item }));
    let debugOrder = graph.nodes.map((node) => node.id);
    let debugIndex = -1;
    let debugActive = false;

    sourceDirInput.value = "";
    outputDirInput.value = "";
    exportFormatInput.value = "terminal";
    exportPathInput.value = "";

    updateInputCount();
    updateOutputCount();
    document.getElementById("graph-summary").textContent = graph.nodes.length + " nodes";
    document.getElementById("flow-type").textContent = graph.flowType || "standard";
    document.getElementById("flow-orchestration").textContent = graph.orchestration || "dag";
    document.getElementById("final-node").textContent = graph.finalNode || "n/a";
    renderInputsTable();
    renderOutputsTable();
    renderYamlOutline();
    initializeBlockToggles();

    const columns = new Map();
    for (const node of graph.nodes) {
      if (!columns.has(node.depth)) columns.set(node.depth, []);
      columns.get(node.depth).push(node);
    }
    const maxRows = Math.max(...Array.from(columns.values(), (items) => items.length), 1);
    const maxDepth = Math.max(...graph.nodes.map((node) => node.depth), 0);
    canvas.style.width = Math.max(760, marginX * 2 + maxRows * columnWidth) + "px";
    canvas.style.height = Math.max(720, marginY * 2 + Math.max(2, maxDepth + 1) * rowHeight + 180) + "px";
    edgesSvg.setAttribute("width", canvas.style.width);
    edgesSvg.setAttribute("height", canvas.style.height);

    const canvasWidth = parseInt(canvas.style.width, 10);
    const inputX = Math.round((canvasWidth - 82) / 2);
    const inputY = 34;
    const outputX = Math.round((canvasWidth - 82) / 2);
    const outputY = marginY + Math.max(1, maxDepth + 1) * rowHeight + 72;
    inputsNode.style.left = inputX + "px";
    inputsNode.style.top = inputY + "px";
    outputsNode.style.left = outputX + "px";
    outputsNode.style.top = outputY + "px";

    const positions = new Map();
    for (const [depth, nodes] of columns.entries()) {
      const totalWidth = nodes.length * columnWidth;
      const startX = Math.max(marginX, Math.round((canvasWidth - totalWidth) / 2));
      nodes.forEach((node, index) => {
        const saved = graph.layout?.positions?.[node.id];
        const x = typeof saved?.x === "number" ? saved.x : startX + index * columnWidth;
        const y = typeof saved?.y === "number" ? saved.y : marginY + depth * rowHeight + 40;
        positions.set(node.id, { x, y });

        const el = document.createElement("button");
        el.className = "node" + (graph.finalNode === node.id ? " final" : "");
        el.style.left = x + "px";
        el.style.top = y + "px";
        el.dataset.nodeId = node.id;
        el.innerHTML =
          '<div class="node-topbar"></div>' +
          '<div class="node-body">' +
            '<div class="node-title"><span class="node-icon"></span><span>' + escapeHtml(node.id) + '</span></div>' +
            '<div class="node-meta"><span class="status-dot"></span><span class="status-label">Idle</span></div>' +
          '</div>';
        el.addEventListener("pointerdown", (event) => beginNodeDrag(event, node.id));
        el.addEventListener("click", (event) => {
          if (dragState?.moved) {
            event.preventDefault();
            event.stopPropagation();
            return;
          }
          selectNode(node.id);
        });
        canvas.appendChild(el);
        nodeElements.set(node.id, el);
        applyNodeStatus(node.id, "idle");
      });
    }

    renderEdges();

    function selectNode(nodeId) {
      const node = graph.nodes.find((item) => item.id === nodeId);
      if (!node) return;
      document.querySelectorAll(".node").forEach((el) => el.classList.toggle("active", el.dataset.nodeId === nodeId));
      document.getElementById("selected-name").textContent = node.id;
      document.getElementById("selected-step").textContent = node.step;
      const status = nodeStatuses.get(node.id) || "idle";
      document.getElementById("selected-status").textContent =
        status === "running" ? "Running" :
        status === "completed" ? (graph.finalNode === node.id ? "Final node" : "Completed") :
        status === "error" ? "Failed" :
        "Idle";
      document.getElementById("selected-deps").textContent = node.depends_on.length ? node.depends_on.join(", ") : "None";
      document.getElementById("selected-config").textContent = JSON.stringify(node.config || {}, null, 2);
    }

    if (graph.nodes.length) {
      selectNode(graph.nodes[0].id);
    }

    function renderEdges() {
      edgeElements.length = 0;
      edgesSvg.innerHTML = "";

      drawPath(null, graph.nodes[0]?.id || null, inputX + 41, inputY + 34, positions.get(graph.nodes[0]?.id)?.x + (cardWidth / 2) || inputX + 41, positions.get(graph.nodes[0]?.id)?.y || (inputY + 100));

      for (const edge of graph.edges) {
        const from = positions.get(edge.source);
        const to = positions.get(edge.target);
        if (!from || !to) continue;
        drawPath(edge.source, edge.target, from.x + (cardWidth / 2), from.y + cardHeight, to.x + (cardWidth / 2), to.y);
      }

      if (graph.finalNode && positions.get(graph.finalNode)) {
        const from = positions.get(graph.finalNode);
        drawPath(graph.finalNode, null, from.x + (cardWidth / 2), from.y + cardHeight, outputX + 41, outputY);
      }
      refreshEdgeStatuses();
    }

    function beginNodeDrag(event, nodeId) {
      if (event.button !== 0) return;
      const el = nodeElements.get(nodeId);
      const position = positions.get(nodeId);
      if (!el || !position) return;
      dragState = {
        nodeId,
        pointerId: event.pointerId,
        startClientX: event.clientX,
        startClientY: event.clientY,
        startX: position.x,
        startY: position.y,
        moved: false
      };
      el.classList.add("dragging");
      el.setPointerCapture(event.pointerId);
      window.addEventListener("pointermove", onNodeDrag);
      window.addEventListener("pointerup", endNodeDrag);
      window.addEventListener("pointercancel", endNodeDrag);
    }

    function onNodeDrag(event) {
      if (!dragState || event.pointerId !== dragState.pointerId) return;
      const el = nodeElements.get(dragState.nodeId);
      const position = positions.get(dragState.nodeId);
      if (!el || !position) return;
      const dx = event.clientX - dragState.startClientX;
      const dy = event.clientY - dragState.startClientY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        dragState.moved = true;
      }
      position.x = Math.max(20, Math.min(canvasWidth - cardWidth - 20, dragState.startX + dx));
      position.y = Math.max(50, Math.min(parseInt(canvas.style.height, 10) - cardHeight - 40, dragState.startY + dy));
      el.style.left = position.x + "px";
      el.style.top = position.y + "px";
      renderEdges();
    }

    function endNodeDrag(event) {
      if (!dragState || event.pointerId !== dragState.pointerId) return;
      const el = nodeElements.get(dragState.nodeId);
      if (el) {
        el.classList.remove("dragging");
        try { el.releasePointerCapture(event.pointerId); } catch (error) {}
      }
      const moved = dragState.moved;
      const nodeId = dragState.nodeId;
      dragState = null;
      window.removeEventListener("pointermove", onNodeDrag);
      window.removeEventListener("pointerup", endNodeDrag);
      window.removeEventListener("pointercancel", endNodeDrag);
      if (!moved) {
        selectNode(nodeId);
      } else {
        scheduleLayoutSave();
      }
    }

    function scheduleLayoutSave() {
      if (layoutSaveTimer) {
        clearTimeout(layoutSaveTimer);
      }
      layoutSaveTimer = setTimeout(() => {
        const positionsPayload = {};
        positions.forEach((value, key) => {
          positionsPayload[key] = { x: Math.round(value.x), y: Math.round(value.y) };
        });
        vscodeApi.postMessage({
          type: "saveLayout",
          payload: {
            flowName: graph.flowName,
            positions: positionsPayload
          }
        });
      }, 180);
    }

    runButton.addEventListener("click", () => {
      debugActive = false;
      debugIndex = -1;
      stepButton.disabled = true;
      setAllStatuses("idle");
      runStatusEl.textContent = "Running flow...";
      vscodeApi.postMessage({
        type: "play",
        payload: {
          sourceDir: sourceDirInput.value.trim(),
          outputDir: outputDirInput.value.trim(),
          exportFormat: exportFormatInput.value,
          exportPath: exportPathInput.value.trim(),
          inputs: flowInputs,
          outputs: flowOutputs
        }
      });
    });

    debugButton.addEventListener("click", () => {
      debugActive = true;
      debugIndex = -1;
      setAllStatuses("idle");
      runStatusEl.textContent = "Debug mode ready";
      stepButton.disabled = false;
    });

    stepButton.addEventListener("click", () => {
      if (!debugActive) return;
      debugIndex += 1;
      if (debugIndex >= debugOrder.length) {
        runStatusEl.textContent = "Debug completed";
        stepButton.disabled = true;
        return;
      }
      const nodeId = debugOrder[debugIndex];
      const node = graph.nodes.find((item) => item.id === nodeId);
      applyNodeStatus(nodeId, "running");
      selectNode(nodeId);
      runStatusEl.textContent = "Debug stepping: " + nodeId;
      setTimeout(() => {
        applyNodeStatus(nodeId, "completed");
        if (debugIndex === debugOrder.length - 1) {
          runStatusEl.textContent = "Debug completed";
          stepButton.disabled = true;
        }
      }, 350);
    });

    addInputButton.addEventListener("click", () => {
      flowInputs.push({ name: "", type: "string", value: "", details: {} });
      renderInputsTable();
      updateInputCount();
    });

    addOutputButton.addEventListener("click", () => {
      flowOutputs.push({ name: "", reference: "" });
      renderOutputsTable();
      updateOutputCount();
    });

    exportFormatInput.addEventListener("change", () => {
      if (exportFormatInput.value === "terminal") {
        exportPathInput.value = "";
        exportPathInput.disabled = true;
        exportPathInput.placeholder = "/path/to/output.json";
      } else {
        exportPathInput.disabled = false;
        exportPathInput.placeholder = "/path/to/output." + exportFormatInput.value;
      }
    });
    exportFormatInput.dispatchEvent(new Event("change"));

    let traceAnimationId = 0;

    window.addEventListener("message", (event) => {
      const message = event.data;
      if (!message || !message.type) return;
      if (message.type === "runStarted") {
        traceAnimationId += 1;
        runStatusEl.textContent = "Running with " + message.sourceDir;
        setAllStatuses("idle");
      } else if (message.type === "runCompleted") {
        runStatusEl.textContent = message.payload.export_path ? ("Exported: " + message.payload.export_path) : "Run completed";
        animateTrace(message.payload.trace || []);
      } else if (message.type === "runError") {
        runStatusEl.textContent = "Run failed";
        stepButton.disabled = true;
        debugActive = false;
        const activeId = debugOrder[Math.max(debugIndex, 0)] || graph.nodes[0]?.id;
        if (activeId) {
          applyNodeStatus(activeId, "error");
          selectNode(activeId);
        }
        document.getElementById("selected-config").textContent = message.message;
      }
    });

    function renderInputsTable() {
      const target = document.getElementById("inputs-table");
      if (!flowInputs.length) {
        target.innerHTML = '<tr><td colspan="3" style="color:var(--muted);">None</td></tr>';
        return;
      }
      target.innerHTML = flowInputs.map((row, index) =>
        '<tr>' +
          '<td><input type="text" data-kind="input-name" data-index="' + index + '" value="' + escapeAttr(row.name || "") + '" /></td>' +
          '<td>' +
            '<select data-kind="input-type" data-index="' + index + '">' +
              renderTypeOptions(row.type || "string") +
            '</select>' +
          '</td>' +
          '<td><input type="text" data-kind="input-value" data-index="' + index + '" value="' + escapeAttr(row.value || "") + '" /></td>' +
        '</tr>'
      ).join("");
      attachTableListeners();
    }

    function renderOutputsTable() {
      const target = document.getElementById("outputs-table");
      if (!flowOutputs.length) {
        target.innerHTML = '<tr><td colspan="2" style="color:var(--muted);">None</td></tr>';
        return;
      }
      target.innerHTML = flowOutputs.map((row, index) =>
        '<tr>' +
          '<td><input type="text" data-kind="output-name" data-index="' + index + '" value="' + escapeAttr(row.name || "") + '" /></td>' +
          '<td><input type="text" data-kind="output-reference" data-index="' + index + '" value="' + escapeAttr(row.reference || "") + '" /></td>' +
        '</tr>'
      ).join("");
      attachTableListeners();
    }

    function attachTableListeners() {
      document.querySelectorAll("[data-kind]").forEach((el) => {
        el.oninput = (event) => {
          const kind = event.target.dataset.kind;
          const index = Number(event.target.dataset.index);
          if (kind === "input-name") flowInputs[index].name = event.target.value;
          if (kind === "input-type") flowInputs[index].type = event.target.value;
          if (kind === "input-value") flowInputs[index].value = event.target.value;
          if (kind === "output-name") flowOutputs[index].name = event.target.value;
          if (kind === "output-reference") flowOutputs[index].reference = event.target.value;
        };
      });
    }

    function updateInputCount() {
      document.getElementById("input-count").textContent = flowInputs.length + " fields";
    }

    function updateOutputCount() {
      document.getElementById("output-count").textContent = flowOutputs.length + " fields";
    }

    function initializeBlockToggles() {
      document.querySelectorAll(".block-header").forEach((header) => {
        const block = header.parentElement;
        header.addEventListener("click", (event) => {
          if (event.target.closest("button")) return;
          block.classList.toggle("collapsed");
        });
      });
    }

    function renderTypeOptions(selected) {
      return ["string", "list", "number", "boolean", "path"].map((value) =>
        '<option value="' + value + '"' + (value === selected ? " selected" : "") + '>' + value + '</option>'
      ).join("");
    }

    function renderYamlOutline() {
      const outline = [];
      let line = 1;
      outline.push(codeLine(line++, '<span class="key">name:</span> <span class="value">' + escapeHtml(graph.flowName) + '</span>'));
      outline.push(codeLine(line++, '<span class="key">flow_type:</span> <span class="value">' + escapeHtml(graph.flowType || "standard") + '</span>'));
      outline.push(codeLine(line++, '<span class="key">orchestration:</span> <span class="value">' + escapeHtml(graph.orchestration || "dag") + '</span>'));
      outline.push(codeLine(line++, '<span class="key">inputs:</span>'));
      for (const input of graph.inputs) {
        outline.push(codeLine(line++, '  <span class="name">' + escapeHtml(input.name) + '</span>:'));
        if (input.type) outline.push(codeLine(line++, '    <span class="key">type:</span> <span class="value">' + escapeHtml(input.type) + '</span>'));
        if (input.value) outline.push(codeLine(line++, '    <span class="key">default:</span> <span class="value">' + escapeHtml(input.value) + '</span>'));
      }
      outline.push(codeLine(line++, '<span class="key">outputs:</span>'));
      for (const output of graph.outputs) {
        outline.push(codeLine(line++, '  <span class="name">' + escapeHtml(output.name) + '</span>:'));
        if (output.type) outline.push(codeLine(line++, '    <span class="key">type:</span> <span class="value">' + escapeHtml(output.type) + '</span>'));
        if (output.reference) outline.push(codeLine(line++, '    <span class="key">reference:</span> <span class="ref">' + escapeHtml(output.reference) + '</span>'));
      }
      outline.push(codeLine(line++, '<span class="key">nodes:</span>'));
      for (const node of graph.nodes) {
        outline.push(codeLine(line++, '- <span class="key">name:</span> <span class="name">' + escapeHtml(node.id) + '</span>'));
        outline.push(codeLine(line++, '  <span class="key">step:</span> <span class="value">' + escapeHtml(node.step) + '</span>'));
        if (node.depends_on.length) {
          outline.push(codeLine(line++, '  <span class="key">depends_on:</span> <span class="ref">[' + escapeHtml(node.depends_on.join(", ")) + ']</span>'));
        }
      }
      document.getElementById("yaml-outline").innerHTML = outline.join("");
    }

    function codeLine(no, html) {
      return '<div class="code-line"><div class="line-no">' + no + '</div><div class="line-text">' + html + '</div></div>';
    }

    function drawPath(sourceId, targetId, startX, startY, endX, endY) {
      const deltaY = endY - startY;
      const curveY = Math.max(18, Math.min(42, Math.abs(deltaY) * 0.28));
      const curveX = Math.max(8, Math.min(22, Math.abs(endX - startX) * 0.22));
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute(
        "d",
        "M " + startX + " " + startY +
        " C " + (startX + curveX) + " " + (startY + curveY) +
        ", " + (endX - curveX) + " " + (endY - curveY) +
        ", " + endX + " " + endY
      );
      path.setAttribute("class", "edge-path edge-idle");
      edgesSvg.appendChild(path);

      const arrow = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
      arrow.setAttribute("points", endX + "," + endY + " " + (endX - 4.5) + "," + (endY - 7.5) + " " + (endX + 4.5) + "," + (endY - 7.5));
      arrow.setAttribute("class", "edge-arrow edge-idle");
      edgesSvg.appendChild(arrow);
      edgeElements.push({ sourceId, targetId, path, arrow });
    }

    function setAllStatuses(status) {
      for (const nodeId of nodeStatuses.keys()) {
        applyNodeStatus(nodeId, status);
      }
      refreshEdgeStatuses();
    }

    function applyNodeStatus(nodeId, status) {
      const el = nodeElements.get(nodeId);
      if (!el) return;
      nodeStatuses.set(nodeId, status);
      el.classList.remove("status-idle", "status-running", "status-completed", "status-error");
      el.classList.add("status-" + status);
      const label = el.querySelector(".status-label");
      if (label) {
        label.textContent =
          status === "running" ? "Running" :
          status === "completed" ? "Completed" :
          status === "error" ? "Failed" :
          "Idle";
      }
      refreshEdgeStatuses();
    }

    function refreshEdgeStatuses() {
      edgeElements.forEach((edge) => {
        const edgeStatus = statusForEdge(edge);
        edge.path.classList.remove("edge-idle", "edge-running", "edge-completed", "edge-success", "edge-error");
        edge.arrow.classList.remove("edge-idle", "edge-running", "edge-completed", "edge-success", "edge-error");
        edge.path.classList.add(edgeStatus);
        edge.arrow.classList.add(edgeStatus);
      });
    }

    function statusForEdge(edge) {
      const sourceStatus = edge.sourceId ? (nodeStatuses.get(edge.sourceId) || "idle") : "completed";
      const targetStatus = edge.targetId ? (nodeStatuses.get(edge.targetId) || "idle") : "completed";
      if (sourceStatus === "error" || targetStatus === "error") return "edge-error";
      if (targetStatus === "running") return "edge-running";
      if ((edge.sourceId && sourceStatus === "completed") && (edge.targetId ? targetStatus === "completed" : true)) return "edge-success";
      if (sourceStatus === "completed") return "edge-completed";
      return "edge-idle";
    }

    function animateTrace(trace) {
      traceAnimationId += 1;
      const animationId = traceAnimationId;
      if (!trace.length) {
        setAllStatuses("completed");
        return;
      }
      setAllStatuses("idle");
      let delay = 0;
      trace.forEach((entry) => {
        setTimeout(() => {
          if (animationId !== traceAnimationId) return;
          applyNodeStatus(entry.node, "running");
          selectNode(entry.node);
          runStatusEl.textContent = "Running: " + entry.node;
        }, delay);
        delay += 350;
        setTimeout(() => {
          if (animationId !== traceAnimationId) return;
          const finalStatus = entry.status === "failed" ? "error" : "completed";
          applyNodeStatus(entry.node, finalStatus);
          runStatusEl.textContent = finalStatus === "error" ? ("Failed: " + entry.node) : ("Completed: " + entry.node);
        }, delay);
        delay += 150;
      });
      setTimeout(() => {
        if (animationId !== traceAnimationId) return;
        finalizeTraceStatuses(trace);
        const failedEntry = trace.find((entry) => entry.status === "failed");
        runStatusEl.textContent = failedEntry ? ("Run failed: " + failedEntry.node) : "Run completed";
      }, delay + 50);
    }

    function finalizeTraceStatuses(trace) {
      const seen = new Set();
      trace.forEach((entry) => {
        const finalStatus = entry.status === "failed" ? "error" : "completed";
        applyNodeStatus(entry.node, finalStatus);
        seen.add(entry.node);
      });
      graph.nodes.forEach((node) => {
        if (!seen.has(node.id) && nodeStatuses.get(node.id) === "running") {
          applyNodeStatus(node.id, "idle");
        }
      });
    }

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function escapeAttr(value) {
      return escapeHtml(value).replace(/"/g, "&quot;");
    }
  </script>
</body>
</html>`;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

module.exports = {
  activate,
  deactivate
};
