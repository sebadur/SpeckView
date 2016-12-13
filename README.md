# SpeckView
Gwyddion Plugin for Spectral Analysis of Band-Excitation measurements. Grid and Voltage-Spectroscopy modes are supported.

## Installation
Copy these files into the directory `~/.gwyddion/pygwy`. You may delte the files `README`, `.gitignore` and `BEDebug.py`
as you won't need them. This software is primarily written for Linux but may work with other operating systems as well
(not tested).

## Usage
This is about fitting a BE-grid with given spectra at each measure point. While the phase is optional
(but recommended) you have to provide an amplitude.

Reads configuration files of a custom *BEv3*-format with ending `.be`. You can find a sample file at
[SpeckView/BE/beispiel.be](/SpeckView/BE/beispiel.be). Missing entries will likely be ignored or evaluated to 0. Both the comma and dot are possible as decimal mark. Nearby this
file there must be the measurement files in *NI*-`.tdms`-format, with possible groups `elstat` or `elmech` and channels `amp` or `phase`.

You will have to save the result in `.gwy` or a related format to open it up again quickly. As long as the measurement
files are beside you will be able to watch the fitted spectra (for amplitude and phase) of it.

## Contributors
Made by these contributors in context of studies for the Justus-Liebig-Universität Gießen:

- Sebastian Badur
- Valon Lushta

This software is part of active studies of science and may only be used or cited in scientific behave. Furthermore we
give no warranty of this software not harming in any way.