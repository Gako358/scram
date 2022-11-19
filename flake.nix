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
      defaultPackage = forAllSystems (system:
        pkgs.${system}.buildEnv {
          name = "gitscram";
          paths = with pkgs.${system}; [
            python39Packages.colorama
            python39Packages.GitPython
            python39Packages.termcolor
          ];
        });
      defaultApp = forAllSystems (system: {
        type = "app";
        program = defaultPackage.${system}/bin/gitscram;
      });
    };
}
