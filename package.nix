with import <nixpkgs> {};
{
  oremi-core = pkgs.poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    python = pkgs.python310;
    groups = [ ]; # TODO Find how to ignore dev dependencies
    preferWheels = false;
    overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend(self: super: {
      pydantic = pkgs.python3Packages.callPackage ./packages/pydantic {};
      pylint-pydantic = pkgs.python3Packages.callPackage ./packages/pylint-pydantic {};
      unqlite = super.unqlite.overridePythonAttrs (
        old: {
          buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
        }
      );
    });
  };
}
