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
            python = pkgs.python310;
            groups = [ ]; # TODO Find how to ignore dev dependencies
            preferWheels = false;
            overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend(self: super: {
              typing-extensions = super.typing-extensions;
            });
          };
        };
        devShell = with pkgs; mkShell {
          EDITOR = "vim";
          PYTHONPATH = ".:${envDir}/${pkgs.python3.sitePackages}:$PYTHONPATH";
          buildInputs = [
            # tmux
            tmuxinator
            tmux
            gitmux
            git

            # python
            poetry
            python310
            python310Packages.pip
            python310Packages.wheel
            python310Packages.twine
            python310Packages.pylint
            python310Packages.pytest-mock
            python310Packages.pytest
            python310Packages.pytest-cov
            python310Packages.pluggy
            python310Packages.pytest-asyncio
            python310Packages.virtualenv
            python310Packages.toml

            # pre-commit
            pre-commit
            ruff
            check-jsonschema
            gnumake
            checkmake
            stdenv.cc.cc.libgcc
            autoPatchelfHook
            which
            nodejs
            python310Packages.pre-commit-hooks
          ];
          shellHook = ''
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
