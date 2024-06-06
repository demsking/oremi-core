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
            python = pkgs.python311;
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
            python311
            python311Packages.pip
            python311Packages.twine
            python311Packages.wheel
            python311Packages.virtualenv

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
            python311Packages.doc8
            python311Packages.autopep8
            python311Packages.pyroma
            python311Packages.pyupgrade
            python311Packages.pre-commit-hooks
            python311Packages.reorder-python-imports
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
