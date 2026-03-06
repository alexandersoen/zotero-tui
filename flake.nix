{
  description = "A TUI for exploring Zotero DB";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        packages.default = python.pkgs.buildPythonApplication {
          pname = "zotero-tui";
          version = "0.1.1";
          pyproject = true;

          # Tells Nix where the source code is
          src = ./.;

          # Build dependencies (Hatchling is required to build the wheel)
          nativeBuildInputs = [
            python.pkgs.hatchling
          ];

          # Runtime dependencies (mapping your TOML to nixpkgs)
          propagatedBuildInputs = with python.pkgs; [
            bibtexparser
            pyperclip
            rapidfuzz
            textual
          ];

          meta = with pkgs.lib; {
            description = "A TUI for exploring Zotero DB";
            homepage = "https://github.com/alexandersoen/zotero-tui";
            license = licenses.mit; # Change if necessary
            mainProgram = "zotero-tui";
          };
        };

        # This lets you run 'nix develop' to get a dev environment
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.uv
            (python.withPackages (
              ps: with ps; [
                bibtexparser
                pyperclip
                rapidfuzz
                textual
                hatchling
              ]
            ))
          ];
        };
      }
    );
}
