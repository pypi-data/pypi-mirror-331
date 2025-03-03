XML Serialization Format
========================

Plugs-in XML support to `masterpiece` applications.

**Note:** This is an alpha release; do not use it for anything critical at this stage.


Usage
-----

To install:

.. code-block:: bash
  
  pip install masterpiece-xmlformat

Once installed, you can pass the `--init` and `--application_serialization_format` 
startup arguments to create a default set of configuration files. For example, to create 
XML configuration files for the 'examples/myapp.py' application:

.. code-block:: bash

  python examples/myapp.py --init --application_serialization_format XMLFormat

Upon successful execution, there should be a file located at `~/.myapp/config/MyApp.xml` 
with the following content:

.. code-block:: xml

  <?xml version='1.0' encoding='utf-8'?>
  <MyApp>
    <solar>0.0</solar>
    <color>yellow</color>
  </MyApp>

To use XML as the default format, add the following line of code to your application:

.. code-block:: python

  Application.serialization_format = "XMLFormat"

License
-------

This project is licensed under the MIT License - see the `LICENSE` file for details.
