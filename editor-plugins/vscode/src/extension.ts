import * as vscode from "vscode";
import { PythonShell } from "python-shell";
import path = require("path");
import cp = require("child_process");
const opn = require("opn");

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.languages.registerDocumentFormattingEditProvider(
        "gdscript",
        {
            provideDocumentFormattingEdits(
                document: vscode.TextDocument
            ): vscode.TextEdit[] {
                let scriptPath = path.resolve(__dirname + "/../scripts/");
                let scriptName = "code_formatter.py";
                let options = PythonShell.defaultOptions;
                options.scriptPath = scriptPath;

                let input = document.getText().replace(/\r\n/g, "\n");
                options.args = [
                    input,
                    `${vscode.workspace.getConfiguration(
                        "gdscript_formatter"
                    ).get("line_size")}`
                ];

                PythonShell.run(scriptName, options, (err, results) => {
                    if (err) {
                        onPythonError(err, document);
                    } else {
                        applyFormat(
                            results ? results.join("\n") : document.getText(),
                            document
                        );
                    }
                });

                return [];
            }
        }
    );

    context.subscriptions.push(disposable);
}

export function runPipInstall(uri: vscode.Uri) {
    cp.exec("pip3 install gdtoolkit", err => {
        if (err) {
            console.log(err);
            vscode.window.showErrorMessage(err.message);
        } else {
            vscode.commands.executeCommand(
                "vscode.executeFormatDocumentProvider",
                uri
            );
        }
    });
}

export function onPythonError(err: Error, document: vscode.TextDocument) {
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
        promise.then(action => {
            if (action === "Open GDToolkit repo") {
                opn("https://github.com/Scony/godot-gdscript-toolkit");
            } else if (action === "Install using pip") {
                runPipInstall(document.uri);
            }
        });
    } else {
        vscode.window.showErrorMessage(message);
    }
}

export function applyFormat(formatted: string, document: vscode.TextDocument) {
    const edit = new vscode.WorkspaceEdit();
    var endLine = document.lineCount - 1;
    var endCharacter = document.lineAt(endLine).text.length - 1;
    if (endCharacter < 0) {
        endCharacter = 0;
    }
    edit.replace(
        document.uri,
        new vscode.Range(
            new vscode.Position(0, 0),
            new vscode.Position(endLine, endCharacter)
        ),
        formatted
    );

    vscode.workspace.applyEdit(edit);
}

export function deactivate() {}
