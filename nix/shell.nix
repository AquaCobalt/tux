{
  mkShell,
  stdenv,
  self,
}:
mkShell {
  inherit (self.checks.${stdenv.system}.pre-commit-check) shellHook;
  buildInputs = self.checks.${stdenv.system}.pre-commit-check.enabledPackages;
}
