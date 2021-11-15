# Release

We release the resulting data as a set of HDT files, a compact binary format that
can be readily accessed and queried using conventional RDF technology, see https://www.rdfhdt.org/.

## How to use it

For *using* HDT data, there are numerous implementations available, including a [GUI](https://www.rdfhdt.org/what-is-hdt/downloads) and plugins
for popular RDF libraries such as [Apache Jena](https://www.rdfhdt.org/development/), and [RDFLib](https://github.com/RDFLib/rdflib-hdt).

For *creating* and *converting* HDT data, we recommend working with the [HDT-CPP libary](https://github.com/rdfhdt/hdt-cpp).
Under Ubuntu 20.04.3 LTS, the installation instructions worked immediately. However, after installation, we had
to run

    $> sudo /sbin/ldconfig -v

to make sure the shared object file `libhdt.so.0` could be found. On an older Ubuntu 18.04.1 LTS, we had to resort to
the [HDT-CPP Docker container](https://hub.docker.com/r/rfdhdt/hdt-cpp/).

To (re-)build the hdt files in this directory, run

  $> make refresh
