{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    { self
    , nixpkgs
    ,
    }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            python39Packages.colorama
            python39Packages.GitPython
            python39Packages.termcolor
          ];
        };
      });
      packages.${system}.scramgit = forAllSystems (system: {
        default = pkgs.${system}.buildPythonPackage rec {
          pname = "scramgit";
          version = "0.1.0";
          src = ./src;
          propagatedBuildInputs = with pkgs.${system}.python39Packages; [
            colorama
            GitPython
            termcolor
          ];
        };
      });
      apps.default = {
        type = "app";
        program = "${self.packages.${system}.scramgit}/bin/scramgit";
      };
    };
}
