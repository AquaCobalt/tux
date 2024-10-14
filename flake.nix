{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
    pre-commit-hooks.url = "github:cachix/git-hooks.nix";
  };
  outputs = inputs @ {
    self,
    nixpkgs,
    ...
  }: let
    systems = ["x86_64-linux" "aarch64-linux"];
    allSystems = nixpkgs.lib.genAttrs systems;
    forAllSystems = f:
      allSystems (system:
        f {
          pkgs = import nixpkgs {inherit system;};
        });
  in {
    checks = allSystems (system: {
      pre-commit-check = inputs.pre-commit-hooks.lib.${system}.run {
        src = self;
        hooks = {
          ruff = {
            enable = true;
            args = ["--fix"];
          };
          ruff-format.enable = true;
          pyright.enable = true;
          pyupgrade.enable = true;
          check-yaml.enable = true;
          check-json.enable = true;
          check-toml.enable = true;
          alejandra.enable = true;
          deadnix = {
            enable = true;
            args = ["--edit"];
          };
          statix.enable = true;
        };
        excludes = ["(^\.archive|/typings)/"];
      };
    });
    devShells = forAllSystems ({pkgs}: {
      default = pkgs.callPackage ./nix/shell.nix {inherit self;};
    });
  };
}
