PyUPnP
======

Simple Python UPnP device library built in Twisted

**NOTE:** PyUPnP doesn't implement ContentDirectory, ConnectionManager, etc.. services.

**We do** provide the shell classes with the actions, state variables and methods, All
you will need to do is inherit the shell class and implement the methods.

See https://github.com/fuzeman/PyUPnP/blob/master/examples/mediaserver/main.py
for an example of how to get started.
