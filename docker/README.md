# levpro-test (with ubuntu 14.04)

[Docker](http://www.docker.com) image configuration for testing [levpro](https://github.com/ska-sa/levpro).

It is based on a [Ubuntu](https://www.ubuntu.com/) 14.04 (trusty) and it provides the following infrastructure for installing and testing levpro:

- xvfb, for headless GUI testing
- levpro dependencies and recommended packages (PyTango, pytest, tango-simlib, Fandango, ...)
- A Tango DB and TangoTest DS configured and running for testing levpro
 
The primary use of this Docker image is to use it in our Continuous Integration workflow.
But you may also run it on your own machine.

First build the image:

~~~~
docker build . -t tango-levpro
~~~~

Start up the tango container:

~~~~
docker run --rm --name tango -v -p 5666:5666 -it tango-levpro:latest
~~~~

or start with levpro project mounted in container for develepment

~~~~
docker run --rm --name levpro -v ../../levpro:/home/tango/src/levpro -p 5666:5666 -it tango-levpro:latest
~~~~

Then you can log into the container with:

~~~~
docker exec -it levpro bash
~~~~

Note: This image does not contain levpro itself (since it is designed for installing development versions of levpro) but you can
install it easily **from your container** (for more details, see [LEvPro Deployment Notes](
https://docs.google.com/document/d/12f495FEMOi0g3bJjoZL3icZaCCr7iSjTY3jToFqA2Ns/edit#heading=h.tzfrhvg9rcoo)).
