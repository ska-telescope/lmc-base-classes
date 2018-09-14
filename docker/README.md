# lmc-base-classes-test (with ubuntu 14.04)

[Docker](http://www.docker.com) image configuration for testing [lmc-base-classes](https://github.com/ska-telescope/lmc-base-classes).

It is based on a [Ubuntu](https://www.ubuntu.com/) 14.04 (trusty) and it provides the following infrastructure for installing and testing lmc-base-classes:

- xvfb, for headless GUI testing
- lmc-base-classes dependencies and recommended packages (PyTango, pytest, tango-simlib, Fandango, ...)
- A Tango DB and TangoTest DS configured and running for testing lmc-base-classes

The primary use of this Docker image is to use it in our Continuous Integration workflow.
But you may also run it on your own machine.

First build the image:

~~~~
docker build . -t tango-lmc-base-classes
~~~~

Start up the tango container:

~~~~
docker run --rm --name lmc-base-classes -it tango-lmc-base-classes:latest
~~~~

or start with lmc-base-classes project (/home/user/src/lmc-base-classes) mounted in container for development

~~~~
docker run --rm --name lmc-base-classes -v /home/user/src/lmc-base-classes:/home/tango-cs/src/lmc-base-classes -it tango-lmc-base-classes:latest
~~~~

or if you want TANGO DB available outside the container, export the port

~~~~
docker run --rm --name lmc-base-classes -v /home/user/src/lmc-base-classes:/home/tango-cs/src/lmc-base-classes -p 10123:10000 -it tango-lmc-base-classes:latest
~~~~

Then you can log into the container with:

~~~~
docker exec -it lmc-base-classes bash
~~~~

Connecting to the TANGO DB using jive

~~~~
env TANGO_HOST=localhost:10123 jive
~~~~

Note: This image does not contain lmc-base-classes itself (since it is designed for installing development versions of lmc-base-classes) but you can
install it easily **from your container** (for more details, see old [LEvPro Deployment Notes](
https://docs.google.com/document/d/12f495FEMOi0g3bJjoZL3icZaCCr7iSjTY3jToFqA2Ns/edit#heading=h.tzfrhvg9rcoo)).
