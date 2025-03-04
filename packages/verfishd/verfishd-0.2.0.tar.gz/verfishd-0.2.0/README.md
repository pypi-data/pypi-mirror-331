<p align="center">
  <img src="https://github.com/marine-data-science/verfishd/blob/main/images/logo/square_logo.png" alt="Logo of VerFishD">
</p>

**VerFishD** is a library to do vertical fish distribution simulations influenced by physical stimuli.
It is still in development and not yet ready for production.

![PyPI - Version](https://img.shields.io/pypi/v/verfishd)
![Successful Tests](https://github.com/marine-data-science/verfishd/actions/workflows/pytest.yml/badge.svg)

## Concept
The library uses `PhysicalFactor` which influence the movement of the fish.
They can be created by implement this base class for your own physical factors like temperature, light, oxygen, et cetera.
The next step would be to load a `StimuliProfile` which is a collection of concrete stimuli values.
The *migration speed* is the function to calculate the final vertical movement of the fish.
The sign of this function determines the direction of the movement and the absolute value the percentage of fish that will move.
All these values are combined in the `VerFishDModel` which is the main class to run the simulation.
The simulation is then triggered by calling the `simulate` method with the number of time steps to simulate.

## Dependencies
To work with .cnv files of CTD casts, the library uses the [`seabird`](https://github.com/castelao/seabird) library.
The profile can be loaded by calling `StimuliProfile.read_from_cnv(file_path)`.

## Example

https://github.com/marine-data-science/verfishd/blob/752e3501ce62ffe1b563d25e3a7783d529d1aba2/Examples/simple_simulation.py#L5-L46

## Installation

```bash
pip install verfishd
```

## Ideas for the future
- [ ] Combine multiple Stimuli Profiles to do a simulation for a whole day
- [ ] Algorithm to determine if simulation can end?
