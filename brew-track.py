#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import subprocess

config_path = \
    Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser() / \
    "brew-track"

def run(argv, pipe = True):
    stdout = subprocess.PIPE if pipe else None
    proc = subprocess.run(argv, stdout = stdout, check = True)
    return proc.stdout.decode("utf-8") if pipe else None

def yesno(prompt, default):
    while True:
        print(prompt, end = "")
        
        decision = input().lower()
        
        if decision in {"y", "yes"}:
            return True
        elif decision in {"n", "no"}:
            return False
        elif decision == "":
            return default

def usage():
    print(
        ("Usage: brew-track install <pkgs...>\n"
         "                  autoremove"),
        file = sys.stderr)
        
    exit(1)

def read_manual_pkgs():
    try:
        with open(config_path / "manual") as f:
            return f.read().split()
    except OSError:
        return []

def write_manual_pkgs(pkgs):
    with open(config_path / "manual", "w") as f:
        f.write("\n".join(pkgs) + "\n")

def install_pkgs(opts, pkgs):
    run(["brew", "install"] + opts + pkgs, pipe = False)
    
    manual_pkgs = set(read_manual_pkgs())
    
    for pkg in pkgs:
        if pkg not in manual_pkgs:
            manual_pkgs.add(pkg)
    
    write_manual_pkgs(manual_pkgs)
    
def autoremove_pkgs():
    manual_pkgs = read_manual_pkgs()
    
    deps = {}
    
    for line in run(["brew", "deps", "--installed", "--1"]).split("\n")[:-1]:
        line_pkg, line_deps = line.split(":")
        deps[line_pkg] = line_deps.split()
    
    visited = set()
    
    for pkg in manual_pkgs:
        autoremove_pkgs_dfs(deps, visited, pkg)
    
    pkgs = run(["brew", "list"]).split()
    
    rm_pkgs = []
    
    for pkg in pkgs:
        if pkg not in visited:
            rm_pkgs.append(pkg)
    
    if len(rm_pkgs) > 0:
        print(
            "Packages to be removed:\n" +
            "\n".join(" * " + pkg for pkg in rm_pkgs))
    
        proceed = yesno("Proceed? [y/N] ", False)
    
        if proceed:
            run(["brew", "rm"] + rm_pkgs, pipe = False)
        else:
            print("Aborted!")
    else:
        print("Nothing to remove.")
    
def autoremove_pkgs_dfs(deps, visited, pkg):
    if pkg in visited:
        return
    
    visited.add(pkg)
    
    for dep in deps[pkg]:
        autoremove_pkgs_dfs(deps, visited, dep)

if __name__ == "__main__":
    config_path.mkdir(parents = True, exist_ok = True)
    
    args = sys.argv[1:]
    
    if len(args) < 1:
        usage()
    
    if args[0] == "install":
        if len(args) < 2:
            usage()
        
        opts = []
        pkgs = []
        
        for arg in args[1:]:
            if arg.startswith("-"):
                opts.append(arg)
            else:
                pkgs.append(arg)
        
        install_pkgs(opts, pkgs)
    elif args[0] == "autoremove":
        if len(args) > 1:
            usage()
        
        autoremove_pkgs()
    else:
        usage()
