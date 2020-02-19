enum LineTypes {
    TOOL,
    CLASS_NAME,
    EXTENDS,
    SIGNAL,
    ENUM,
    CONST,
    EXPORT,
    PUBLIC_VAR,
    PRIVATE_VAR,
    ONREADY,
    INIT,
    READY,
    BUILT_IN,
    PUBLIC_FUNC,
    PRIVATE_FUNC,
    CLASS_DOCSTRING
}

const TYPE_MATCHES = [
    new RegExp(/^tool/),
    new RegExp(/^class_name/),
    new RegExp(/^extends/),
    new RegExp(/^signal/),
    new RegExp(/^enum/),
    new RegExp(/^const/),
    new RegExp(/^export/),
    new RegExp(/^var [a-zA-Z]/),
    new RegExp(/^var _/),
    new RegExp(/^onready/),
    new RegExp(/^func _init/),
    new RegExp(/^func _ready/),
    new RegExp(/^func _/),
    new RegExp(/^func [a-zA-Z]/),
    new RegExp(/^func _/)
];

const BUILTIN_VIRTUAL_CALLBACKS = [
    "_process",
    "_physics_process",
    "_input",
    "_unhandled_input",
    "_gui_input",
    "_draw",
    "_get_configuration_warning",
    "_enter_tree",
    "_exit_tree",
    "_get",
    "_get_property_list",
    "_notification",
    "_set",
    "_to_string",
    "_clips_input",
    "_get_minimum_size",
    "_gui_input",
    "_make_custom_tooltip"
];

interface ParsedBlock {
    block: string[];
    from: number;
    to: number;
    type: number;
}

export class Organizer {
    private parsed_objects: ParsedBlock[] = [];
    private script_objects: string[];
    private class_docstring: string[] = [];
    private start_index = 0;

    constructor(script_objects: string[]) {
        this.script_objects = script_objects;
        this.save_class_docstring();
        this.parse_script();
        this.sort_script();
    }

    public get_parsed_script() {
        let script = "";
        if (this.class_docstring.length > 0) {
            script += `${this.class_docstring.join("\n")}\n`;
        }
        let last_type = this.parsed_objects[0].type;
        this.parsed_objects.forEach(po => {
            if(po.type !== last_type || script[script.length-1] !== '\n') {
                script += '\n';
                last_type = po.type;
            }
            script += `${po.block.join("\n")}`;
        });

        return script;
    }

    private save_class_docstring() {
        for (let i = 0; i < this.script_objects.length; ++i) {
            let line = this.script_objects[i];
            let match = line.match(new RegExp(/^(#|""").*?$/));
            if (match) {
                let diff = this.parse_next_comment(i, true);
                this.class_docstring = this.parsed_objects.shift()?.block || [];
                this.start_index = diff + 1;
                return;
            }
        }
    }

    private get_commented_index(index: number) {
        let commented_index = index;

        commented_index = index - 1;
        for (; commented_index > 0; --commented_index) {
            let line = this.script_objects[commented_index];
            let match_index = TYPE_MATCHES.findIndex(tm => line.match(tm));
            if (match_index !== -1 || line.charAt(0).match(/[\t\}\)]/)) {
                commented_index++;
                break;
            }
        }

        return commented_index;
    }

    private parse_next(
        index: number,
        type: LineTypes,
        skip_docstring: boolean
    ) {
        let commented_index = index;
        if (!skip_docstring) {
            commented_index = this.get_commented_index(index);
        }

        for (
            let i = index + 1, count = 0;
            i < this.script_objects.length;
            ++i, ++count
        ) {
            let done =
                TYPE_MATCHES.findIndex(tm =>
                    this.script_objects[i].match(tm)
                ) !== -1;
            if (done) {
                this.put_lines_into(commented_index, i, type);
                return count;
            } else {
                if (i === this.script_objects.length - 1) {
                    this.put_lines_into(
                        commented_index,
                        this.script_objects.length,
                        type
                    );
                    return count;
                } else {
                    if (
                        this.script_objects[i].charAt(0) === "#" ||
                        this.script_objects[i].slice(0, 3) === '"""'
                    ) {
                        this.put_lines_into(commented_index, i, type);
                        return count;
                    }
                }
            }
        }

        console.error("Unreachable code");
        return 0;
    }

    private parse_next_comment(index: number, grab_docstring?: boolean) {
        let multiline = this.script_objects[index].slice(0, 3) === '"""';

        for (
            let i = index, count = 0;
            i < this.script_objects.length;
            ++i, count++
        ) {
            let done = false;
            if (i === this.script_objects.length - 1) {
                done = true;
            } else {
                if (multiline) {
                    if (this.script_objects[i + 1].match(/"""/)) {
                        done = true;
                    }
                } else {
                    if (this.script_objects[i + 1].charAt(0) !== "#") {
                        done = true;
                    }
                }
            }
            if (done) {
                if (i !== this.script_objects.length - 1) {
                    let match_index = TYPE_MATCHES.findIndex(tm =>
                        this.script_objects[i + 1].match(tm)
                    );
                    if (match_index !== -1 && !grab_docstring) {
                        // Is a docstring
                        return 0;
                    }
                }

                this.put_lines_into(index, i + 1, LineTypes.CLASS_DOCSTRING);
                return count;
            }
        }

        console.error("Unreachable code for comments.");
        return 0;
    }

    private parse_next_function(index: number, skip_docstring: boolean) {
        let signature = this.script_objects[index].slice(5);
        let function_name = signature.split("(")[0];

        if (BUILTIN_VIRTUAL_CALLBACKS.indexOf(function_name) !== -1) {
            return this.parse_next(index, LineTypes.BUILT_IN, skip_docstring);
        } else {
            return this.parse_next(
                index,
                LineTypes.PRIVATE_FUNC,
                skip_docstring
            );
        }
    }

    private parse_script() {
        let script_length = this.script_objects.length;
        let start = true;

        for (let i = this.start_index; i < script_length; i++) {
            let line = this.script_objects[i];

            let match_index = TYPE_MATCHES.findIndex(tm => line.match(tm));
            if (match_index !== -1) {
                let diff = 0;
                if (match_index === LineTypes.BUILT_IN) {
                    if (start) {
                        diff = this.parse_next_function(
                            i,
                            this.class_docstring.length > 0
                        );
                    } else {
                        diff = this.parse_next_function(i, false);
                    }
                } else {
                    if (start) {
                        diff = this.parse_next(
                            i,
                            match_index,
                            this.class_docstring.length > 0
                        );
                    } else {
                        diff = this.parse_next(i, match_index, false);
                    }
                }

                i += diff;
            }
            start = false;
        }
    }

    private put_lines_into(from: number, to: number, type: LineTypes) {
        let block: string[] = this.script_objects.slice(from, to);

        for (let i = block.length - 1; i > 0; --i) {
            let match_index = TYPE_MATCHES.findIndex(tm => block[i].match(tm));
            if (match_index === -1) {
                if (block[i].length === 0) {
                    block.pop();
                }
            } else {
                break;
            }
        }

        this.parsed_objects.push({
            block: block,
            type: type,
            from: from,
            to: to
        });
    }

    private sort(a: ParsedBlock, b: ParsedBlock) {
        let a_type = a.type;
        let b_type = b.type;

        return a_type - b_type;
    }

    private sort_script() {
        this.parsed_objects = this.parsed_objects.slice(0).sort(this.sort);
    }
}
