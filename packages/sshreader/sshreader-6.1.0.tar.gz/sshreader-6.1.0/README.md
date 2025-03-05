# [sshreader][]

## Overview

[SSHreader][] is a Python Module for multiprocessing/threading ssh connections in order to make ssh operations
across multiple servers parallel.  It utilizes the [Paramiko](http://www.paramiko.org/) module for its ssh client.

In order to maintain the widest range of compatibility, [SSHreader][] is currently tested using the following versions of
Python:

* Python3.9
* Python3.10
* Python3.11
* Python3.12
* Python3.13

## License

[SSHreader][] is released under [GNU Lesser General Public License v3.0][],
see the file LICENSE and LICENSE.lesser for the license text.

## Installation

The most straightforward way to get the [SSHreader][] module working for you is:

```commandline
pip install sshreader
```

This ensures that all the requirements are met.

## Documentation

The documentation for [SSHreader][] can be found [here](https://sshreader.readthedocs.io)


## Contributing

Comments and enhancements are very welcome.

Report any issues or feature requests on the [BitBucket bug
tracker](https://bitbucket.org/isaiah1112/sshreader/issues?status=new&status=open). Please include a minimal
(not-) working example which reproduces the bug and, if appropriate, the
 traceback information.  Please do not request features already being worked
towards.

Code contributions are encouraged: please feel free to [fork the
project](https://bitbucket.org/isaiah1112/sshreader) and submit pull requests to the develop branch.

### Development Installation

If you are wanting to work on development of [SSHreader][], first ensure [Poetry](https://python-poetry.org) is installed
and then:

```commandline
poetry install --with dev
```

To ensure all development requirements are met. This will allow you to run the unit/integration tests!

### Building Docs

If you have installed [Poetry](https://python-poetry.org)] you can build its Sphinx Documentation for [SSHreader][] simply by:

```commandline
make docs
```

Then simply open `docs/build/html/index.html` in your browser.

## Extras

Included with sshreader is a script called `pydsh`.  This works very similar to[pdsh](https://computing.llnl.gov/linux/pdsh.html) 
but uses sshreader at its core to perform ssh commands in parallel and return the results.  
The output of `pydsh` can also be piped through the `dshbak` tool that comes with pdsh.

Pydsh uses [hostlist expressions](https://www.nsc.liu.se/~kent/python-hostlist/) to get its list of hosts
to process.


[GNU Lesser General Public License v3.0]: http://choosealicense.com/licenses/lgpl-3.0/ "LGPL v3"

[sshreader]: https://bitbucket.org/isaiah1112/sshreader "SSHreader Package"
