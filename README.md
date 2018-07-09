# brew-track

A little tool that implements `apt autoremove` for [Homebrew](https://brew.sh).
It removes packages that neither were manually installed nor are needed
dependencies of those that were.

## Usage

	$ brew-track install runit
	...
	$ brew-track autoremove
	Nothing to remove.
	$ sed -i '' '/^runit$/d' ~/.config/brew-track/manual
	$ brew-track autoremove
	Packages to be removed:
	 * runit
	Proceed? [y/N] y
	Uninstalling /usr/local/Cellar/runit/2.1.2... (20 files, 263.8KB)
