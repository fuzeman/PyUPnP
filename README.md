PyUPnP
======
*Simple Python UPnP device library built in Twisted*

**NOTE:** PyUPnP doesn't implement ContentDirectory, ConnectionManager, etc.. services.

**We do** provide some shell classes with the actions, state variables and method signatures
already setup as per the UPnP spec, So all you need to do is inherit the shell class and
implement the methods.

See https://github.com/fuzeman/PyUPnP/blob/master/examples/mediaserver/main.py
for an example of how to get started.

### Debugging / Logging ###

To enable debugging just call the following

     Logr.configure(logging.DEBUG)

----

     def configure(level=logging.WARNING, handler=None, formatter=None)

If **handler** is None it defaults to `logging.StreamHandler`

If **formatter** is None it defaults to an internal formatter found in the `logr` module
