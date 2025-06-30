{
  description =
    "set of tools for working with GDScript: parser, linter, formatter and code analysis";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonWithPkgs = pkgs.python3.withPackages
          (ps: with ps; [ lark docopt-ng pyyaml radon setuptools ]);

        appVersion = "4.3.4";

        helpScript = pkgs.writeShellScript "gdtoolkit-help" ''
          echo "GDScript Toolkit - Available commands:"
          echo ""
          echo "Usage: nix run github:Scony/godot-gdscript-toolkit#<command> -- [args]"
          echo ""
          echo "Available commands:"
          echo "  gdparse   - GDScript parser for debugging and educational purposes"
          echo "  gdlint    - GDScript linter that performs static analysis"
          echo "  gdformat  - GDScript formatter that formats code according to predefined rules"
          echo "  gdradon   - GDScript code complexity analysis (calculates cyclomatic complexity)"
          echo ""
          echo "Examples:"
          echo "  nix run github:Scony/godot-gdscript-toolkit#gdformat -- --help"
          echo "  nix run github:Scony/godot-gdscript-toolkit#gdlint -- myfile.gd"
          echo "  nix run github:Scony/godot-gdscript-toolkit#gdparse -- myfile.gd -p"
          echo ""
          echo "For local development:"
          echo "  nix develop  # Enter development shell with all tools available"
        '';
      in {
        packages = {
          gdtoolkit = pkgs.python3.pkgs.buildPythonPackage {
            pname = "gdtoolkit";
            version = appVersion;
            src = self;

            propagatedBuildInputs = with pkgs.python3.pkgs; [
              lark
              docopt-ng
              pyyaml
              radon
              setuptools
            ];

            # Create console scripts
            postInstall = ''
              mkdir -p $out/bin
              echo '#!/usr/bin/env python' > $out/bin/gdparse
              echo 'import sys; from gdtoolkit.parser.__main__ import main; sys.exit(main())' >> $out/bin/gdparse
              echo '#!/usr/bin/env python' > $out/bin/gdlint
              echo 'import sys; from gdtoolkit.linter.__main__ import main; sys.exit(main())' >> $out/bin/gdlint
              echo '#!/usr/bin/env python' > $out/bin/gdformat
              echo 'import sys; from gdtoolkit.formatter.__main__ import main; sys.exit(main())' >> $out/bin/gdformat
              echo '#!/usr/bin/env python' > $out/bin/gdradon
              echo 'import sys; from gdtoolkit.gdradon.__main__ import main; sys.exit(main())' >> $out/bin/gdradon
              chmod +x $out/bin/*
            '';
          };

          default = self.packages.${system}.gdtoolkit;
        };

        apps = {
          help = {
            type = "app";
            program = "${helpScript}";
            meta = with pkgs.lib; {
              description = "Show available GDScript Toolkit commands";
              homepage = "https://github.com/Scony/godot-gdscript-toolkit";
              license = licenses.mit;
              platforms = platforms.all;
            };
          };

          gdparse = {
            type = "app";
            program = "${self.packages.${system}.gdtoolkit}/bin/gdparse";
            meta = with pkgs.lib; {
              description = "GDScript parser";
              homepage = "https://github.com/Scony/godot-gdscript-toolkit";
              license = licenses.mit;
              platforms = platforms.all;
            };
          };

          gdlint = {
            type = "app";
            program = "${self.packages.${system}.gdtoolkit}/bin/gdlint";
            meta = with pkgs.lib; {
              description = "GDScript linter";
              homepage = "https://github.com/Scony/godot-gdscript-toolkit";
              license = licenses.mit;
              platforms = platforms.all;
            };
          };

          gdformat = {
            type = "app";
            program = "${self.packages.${system}.gdtoolkit}/bin/gdformat";
            meta = with pkgs.lib; {
              description = "GDScript formatter";
              homepage = "https://github.com/Scony/godot-gdscript-toolkit";
              license = licenses.mit;
              platforms = platforms.all;
            };
          };

          gdradon = {
            type = "app";
            program = "${self.packages.${system}.gdtoolkit}/bin/gdradon";
            meta = with pkgs.lib; {
              description = "GDScript code complexity analysis";
              homepage = "https://github.com/Scony/godot-gdscript-toolkit";
              license = licenses.mit;
              platforms = platforms.all;
            };
          };

          default = self.apps.${system}.help;
        };

        devShells = {
          default = pkgs.mkShell {
            name = "gdtoolkit-dev-env";
            packages = [ pythonWithPkgs ];

            shellHook = ''
              export HISTFILE=$HOME/.history_nix
              export PYTHONPATH=${builtins.toString ./.}:$PYTHONPATH
              export PATH=${pythonWithPkgs}/bin:$PATH
              alias gdparse="python -m gdtoolkit.parser"
              alias gdlint="python -m gdtoolkit.linter"
              alias gdformat="python -m gdtoolkit.formatter"
              alias gdradon="python -m gdtoolkit.gdradon"
              echo "GDScript Toolkit development environment activated"
              echo "Available commands: gdparse, gdlint, gdformat, gdradon"
            '';
          };
        };
      });
}
