{
  description = "Oremi Core";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        envDir = "./venv";
        pkgs = import nixpkgs { inherit system; };
      in
      {
        packages = rec {
          default = pkgs.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            python = pkgs.python312;
            groups = [ ]; # TODO Find how to ignore dev dependencies
            preferWheels = false;
            overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend(self: super: {
              typing-extensions = super.typing-extensions;
            });
          };
        };
        devShell = with pkgs; mkShell {
          EDITOR = "vim";
          SKIP = "insert-license";
          PYTHONPATH = ".:${envDir}/${pkgs.python3.sitePackages}:$PYTHONPATH";
          buildInputs = [
            # tmux
            git
            tmux
            gitmux
            tmuxinator

            # python
            dart
            poetry
            python312
#             python312Packages.pip
#             python312Packages.wheel
#             python312Packages.virtualenv

            # tests
            nodePackages.nodemon

            # certificates
            openssl

            # pre-commit
            ruff
            which
            nodejs
            hadolint
            check-jsonschema
            gnumake
            bandit
            skjold
            shellcheck
            prospector
            pre-commit
            editorconfig-checker
#             python312Packages.doc8
#             python312Packages.autopep8
#             python312Packages.pyroma
#             python312Packages.pyupgrade
#             python312Packages.pre-commit-hooks
#             python312Packages.reorder-python-imports
          ];
          shellHook = ''
            # Disable Dart analytics
            dart --disable-analytics > /dev/null

            # Python
            virtualenv `basename ${envDir}`
            VIRTUAL_ENV_DISABLE_PROMPT=true source ${envDir}/bin/activate

            # Node.js
            mkdir -p .nix-node
            export NODE_PATH=$PWD/.nix-node
            export PATH=$NODE_PATH/bin:$PATH
            npm config set prefix $NODE_PATH

            if ! which gimtoc &> /dev/null; then
              npm install -g gimtoc
            fi

            # Install pre-commit hooks
            pre-commit install -f
          '';
        };
      });
}
