import * as vscode from "vscode";
import { Options, PythonShell } from "python-shell";
import path = require("path");
import cp = require("child_process");
import { Organizer } from "./Organizer";
const opn = require("opn");

const SCRIPT_PATH = path.resolve(__dirname + "/../scripts/");
const SCRIPT_NAME = "code_formatter.py";

const PY_ARGS = [
    "",
    `${vscode.workspace
        .getConfiguration("gdscript_formatter")
        .get("line_size")}`,
];

export function activate(context: vscode.ExtensionContext) {
    let organize_command = vscode.commands.registerCommand(
        "gdscript-formatter.organize_script",
        async () => {
            if (vscode.window.activeTextEditor) {
                let document = vscode.window.activeTextEditor.document;
                let results = await run_formatter(document.getText(), document.uri);
                if (results) {
                    let organizer = new Organizer(results);
                    let organized = await run_formatter(
                        organizer.get_parsed_script(),
                        document.uri
                    );

                    applyFormat(
                        organized
                            ? organized.join("\n")
                            : document.getText(),
                        document
                    );
                }
            }
        }
    );

    let convert_command = vscode.commands.registerCommand(
        "gdscript-formatter.convert_multiline",
        () => {
            if (vscode.window.activeTextEditor) {
                let document = vscode.window.activeTextEditor.document;
                let script = replace_multiline(document.getText());
                applyFormat(script, document);
            }
        }
    );

    let formatter = vscode.languages.registerDocumentFormattingEditProvider(
        "gdscript",
        {
            provideDocumentFormattingEdits(
                document: vscode.TextDocument
            ): Promise<vscode.TextEdit[]> {
                return provideEdits(document);
            },
        }
    );

    let update_formatter = vscode.commands.registerCommand(
        "gdscript-formatter.update_formatter",
        () => {
            runPipInstall();
        }
    );

    context.subscriptions.push(update_formatter);
    context.subscriptions.push(formatter);
    context.subscriptions.push(organize_command);
    context.subscriptions.push(convert_command);
}

export async function run_formatter(
    script: string,
    uri: vscode.Uri
): Promise<string[] | undefined> {
    let options = PythonShell.defaultOptions;
    options.scriptPath = SCRIPT_PATH;

    const pythonConfig = vscode.workspace.getConfiguration("python");
    for (const pathSettingKey of ["defaultInterpreterPath", "pythonPath"]) {
        const pythonPath: string | undefined = pythonConfig.get(pathSettingKey);
        if (!!pythonPath) {
            options.pythonPath = pythonPath;
            break;
        }
    }

    let input = script;

    options.args = PY_ARGS;
    options.args[0] = input;
    try {
        return await runPythonCommand(options);
    } catch (error) {
        onPythonError(error as Error, uri);
    }
}

function runPythonCommand(options: Options) {
    return new Promise<string[] | undefined>((resolve, reject) => {
        PythonShell.run(SCRIPT_NAME, options, (err, results) => {
            if (err) {
                reject(err);
            } else {
                resolve(results);
            }
        });
    });
}

export function replace_multiline(script: string) {
    let comment_blocks = script.match(/^"""[\s\S]*?"""/);
    if (!comment_blocks) {
        return script;
    }

    let replacement_blocks: string[] = [];

    comment_blocks?.forEach((cb) => {
        let uncommented = cb.slice(3, cb.length - 3);
        let lines = uncommented.split("\n");
        let final_block = "";
        let start_line = lines[0];
        let end_line = lines[lines.length - 1];
        let start_index = start_line.length === 0 ? 1 : 0;
        let end_index = end_line.length === 0 ? lines.length - 1 : lines.length;
        if (end_index > start_index) {
            lines.slice(start_index, end_index).forEach((l, i, arr) => {
                final_block += `# ${l}${i < arr.length - 1 ? "\n" : ""}`;
            });
        } else {
            final_block = `# ${lines[start_index]}`;
        }
        replacement_blocks.push(final_block);
    });

    replacement_blocks.forEach((rb, i) => {
        if (comment_blocks) {
            script = script.replace(new RegExp(comment_blocks[i]), rb);
        }
    });

    return script;
}

export function runPipInstall(uri?: vscode.Uri) {
    cp.exec("pip3 install gdtoolkit", (err) => {
        if (err) {
            console.log(err);
            vscode.window.showErrorMessage(err.message);
        } else if (uri) {
            vscode.commands.executeCommand(
                "vscode.executeFormatDocumentProvider",
                uri
            );
        }
    });
}

export function onPythonError(err: Error, uri: vscode.Uri) {
    console.log(err);
    var message = err.message;
    if (
        message.indexOf("ModuleNotFoundError") !== -1 &&
        message.indexOf("gdtoolkit") !== -1
    ) {
        let promise = vscode.window.showErrorMessage(
            "GDToolkit not installed.",
            "Install using pip",
            "Open GDToolkit repo"
        );
        promise.then((action) => {
            if (action === "Open GDToolkit repo") {
                opn("https://github.com/Scony/godot-gdscript-toolkit");
            } else if (action === "Install using pip") {
                runPipInstall(uri);
            }
        });
    } else {
        vscode.window.showErrorMessage(message);
    }
}

async function provideEdits(document: vscode.TextDocument) {
    var edits: vscode.TextEdit[] = [];
    var endLine = document.lineCount - 1;
    var end_character = document.lineAt(endLine).text.length;
    var range = new vscode.Range(0, 0, endLine, end_character);

    const results = await run_formatter(document.getText(), document.uri);
    if (results) {
        edits.push(vscode.TextEdit.replace(range, results.join('\n')));
    }

    return edits;
}

export function applyFormat(formatted: string, document: vscode.TextDocument) {
    const edit = new vscode.WorkspaceEdit();
    var endLine = document.lineCount - 1;
    var end_character = document.lineAt(endLine).text.length;
    edit.replace(
        document.uri,
        new vscode.Range(
            new vscode.Position(0, 0),
            new vscode.Position(endLine, end_character)
        ),
        formatted
    );
    vscode.workspace.applyEdit(edit);
}

export function deactivate() { }
