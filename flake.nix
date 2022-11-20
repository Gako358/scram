{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self
    , nixpkgs
    , flake-utils
    ,
    }:
    flake-utils.lib.eachSystem [ "x86_64-linux" ] (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };

      scramgit = pkgs.python39Packages.buildPythonApplication {
        pname = "scramgit";
        version = "0.1.0";
        src = ./src;
        propagatedBuildInputs = with pkgs.python39Packages; [
          colorama
          GitPython
          termcolor
        ];

        meta = {
          description = "A simple git wrapper to help you keep your git history clean";
          license = pkgs.lib.licenses.mit;
          maintainers = with pkgs.lib.maintainers; [ merrinx ];
        };
      };
    in
    {
      packages.scramgit = scramgit;
      packages.default = self.packages.${system}.scramgit;

      apps.scramgit = {
        type = "app";
        program = "${self.packages.${system}.scramgit}/bin/scramgit";
      };

      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          python39Packages.colorama
          python39Packages.GitPython
          python39Packages.termcolor
        ];
      };
    });
}
