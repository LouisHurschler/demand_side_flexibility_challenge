{
  description = "minimal cpp flake.nix";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };
    in
    {
      formatter.${system} = pkgs.nixpkgs-fmt;

      devShell.${system} = pkgs.mkShell rec {
        nativeBuildInputs = with pkgs; [


          (python3.withPackages (ps: with ps;
          [
            python-lsp-server
            ipython
            black

            numpy
            pandas
            tkinter
            plotly
          ]))
        ];
        buildInputs = with pkgs; [ 
        ];

        CPATH = pkgs.lib.makeSearchPathOutput "dev" "include" buildInputs;
        LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath buildInputs;
      };
    };
}
