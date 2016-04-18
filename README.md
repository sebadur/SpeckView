# SpeckView
Gwyddion Plugin for Spectral Analysis of Band-Excitation or TERS measurements.

## Installation
Copy these files into the directory `~/.gwyddion/pygwy`. You may delte the files `README`, `.gitignore` and `BEDebug.py`
as you won't need them. This software is primarily written for Linux but may work with other operating systems as well
(not tested).

## Usage

### Band-Excitation
This part of SpeckView is about fitting a BE-grid with given spectra at each measure point. While the phase is optional
(but recommended) you have to provide an amplitude.

Reads configuration files of type `format="BE-Raster"` with ending `.ber`. You can find a sample file at
[SpeckView/BE/beispiel.ber](/SpeckView/BE/beispiel.ber). Note that you can customize the name of each logging-entry to
your wishes. Missing entries will be evaluated to 0. Both the comma and dot are possible as decimal mark. Nearby this
file there (currently) must be the measurement files in *NI*-`.tdms`-format, while you are able to name group and
channel for each specific measurement.

You will have to save the result in `.gwy` or a related format to open it up again quickly. As long as the measurement
files are beside you will be able to watch the fitted spectra (for amplitude and phase) of it.
*Note: Currently you may not be able to review fitted spectra after changing files directories due to a minor bug.*

### TERS-Import
This plugin is under development and can't be used yet.

## Contributors
Made by these contributors in context of studies for the Justus-Liebig-Universität Gießen:

- Valon Lushta
- Sebastian Badur
- Jalmar Tschakert

This software is part of active studies of science and may only be used or cited in scientific behave. Furthermore we
give no warranty of this software not harming in any way.