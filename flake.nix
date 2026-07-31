{
  description = "SKALE validator CLI — sk-val";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];

      perSystem = { pkgs, ... }:
        let
          commit = let
            buildCommit = builtins.getEnv "SK_VAL_BUILD_COMMIT";
          in
            if buildCommit != "" then buildCommit else inputs.self.rev or inputs.self.dirtyRev or "not captured by Nix";
          buildDate = let
            buildTimestamp = builtins.getEnv "SK_VAL_BUILD_DATETIME";
          in
            if buildTimestamp != "" then buildTimestamp else inputs.self.lastModifiedDate or "not captured by Nix";
          buildBranch = let
            branch = builtins.getEnv "SK_VAL_BUILD_BRANCH";
          in
            if branch != "" then branch else "not captured by Nix";
          version     = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project.version;

          workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          overlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          ## Packages that require non-Python build-time inputs or undeclared
          ## build-system deps. All setuptools-only cases share the same root cause:
          ## the package uses setuptools.build_meta but omits setuptools from its
          ## [build-system].requires, so Nix fails with ModuleNotFoundError under
          ## --no-build-isolation.
          pyprojectOverrides = final: prev:
            let
              withSetuptools = pkg: pkg.overrideAttrs (old: {
                nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ final.setuptools ];
              });
            in
            {
              # C extension; additionally needs swig and openssl at build time.
              m2crypto = prev.m2crypto.overrideAttrs (old: {
                nativeBuildInputs = (old.nativeBuildInputs or []) ++ [
                  pkgs.swig
                  final.setuptools
                ];
                buildInputs = (old.buildInputs or []) ++ [
                  pkgs.openssl
                  pkgs.openssl.dev
                ];
                SWIG_FEATURES = "-cpperraswarn -includeall -I${pkgs.openssl.dev}/include";
                LDFLAGS = "-L${pkgs.openssl.out}/lib";
              });

              python-baseconv = withSetuptools prev.python-baseconv;
              varint           = withSetuptools prev.varint;
              bitarray         = withSetuptools prev.bitarray;

              # cli/info.py is gitignored (generated at PyInstaller build time).
              # Nix generates it here with real values from the flake evaluation
              # context: self.rev for the commit hash, self.lastModifiedDate for
              # the build timestamp, stdenv.system for the platform string, and
              # SK_VAL_BUILD_* env overrides for release pipelines that need
              # explicit provenance. Nix does not expose the source branch to
              # flake expressions by default, and dirty local flake builds can
              # omit rev.
              "validator-cli" = prev."validator-cli".overrideAttrs (old: {
                postPatch = (old.postPatch or "") + ''
                  rm -rf build dist *.egg-info

                  cat > cli/info.py <<'NIXEOF'
                  BUILD_DATETIME = ${builtins.toJSON buildDate}
                  COMMIT = ${builtins.toJSON commit}
                  BRANCH = ${builtins.toJSON buildBranch}
                  OS = ${builtins.toJSON pkgs.stdenv.system}
                  VERSION = ${builtins.toJSON version}
                  NIXEOF
                '';
              });
            };

          python = pkgs.python314;

          pythonSet = (pkgs.callPackage inputs.pyproject-nix.build.packages {
            inherit python;
          }).overrideScope (
            pkgs.lib.composeManyExtensions [
              inputs.pyproject-build-systems.overlays.default
              overlay
              pyprojectOverrides
            ]
          );

          venv = pythonSet.mkVirtualEnv "validator-cli-env" (workspace.deps.default // {
            setuptools = [];
          });
        in
        {
          ## Nix package — `nix profile install` / `nix run`
          ## Exposes only the sk-val binary so the venv's python3/python3.14 and
          ## other interpreter symlinks don't conflict with home-manager or system
          ## Python entries in the user's Nix profile.
          packages.default = pkgs.runCommand "sk-val" {
            meta = { mainProgram = "sk-val"; };
          } ''
            mkdir -p $out/bin
            ln -s ${venv}/bin/sk-val $out/bin/sk-val
          '';

          ## Dev shell — used by CI for macOS ARM builds.
          ## Provides swig + openssl so `uv sync` can compile m2crypto.
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              swig
              openssl
              openssl.dev
              uv
              python314
            ] ++ pkgs.lib.optionals pkgs.stdenv.isLinux [
              libusb1
            ];

            shellHook = ''
              export LDFLAGS="-L${pkgs.openssl.out}/lib"
              export CFLAGS="-I${pkgs.openssl.dev}/include"
              export SWIG_FEATURES="-cpperraswarn -includeall -I${pkgs.openssl.dev}/include"
            '';
          };
        };
    };
}
