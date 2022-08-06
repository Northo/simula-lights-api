# Lights at KA23

Command line tool for controlling the lights as KA23.

## Install
You can install the package with [`pipx`](https://github.com/pypa/pipx)

```
pipx install git+https://github.com/ComputationalPhysiology/simula-lights
```

This will install the `lights` command.

## Usage
You must give your office number as the first argument:

```
lights ROOM
```

With no other arguments, the lights are reset:

```
lights ROOM
```

You can also specify brightness or color with a range 0-4:

```
lights ROOM brightness 2
```
or
```
lights ROOM color 3
```

## Credits

The script is written by [minrk](https://github.com/minrk) and packaged by [finsberg](https://github.com/finsberg)