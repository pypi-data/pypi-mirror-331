Yaml Serialization Format
=========================

Plugs in  **Yaml** support to `masterpiece` applications.

**Note:** This is an alpha release; do not use it for anything critical at this stage.


Usage
-----

To install:

.. code-block:: bash

  pip install masterpiece-yamlformat

Once installed, you can pass the `--init` and `--application_serialization_format` 
startup arguments to create a default set of configuration files. For example, to create 
yaml configuration files for the 'examples/myapp.py' application:

.. code-block:: bash

  python examples/myapp.py --init --application_serialization_format YamlFormat

Upon successful execution, there should be a file located at `~/.myapp/config/MyApp.yaml`.

To use yaml as the default format, add the following line of code to your application:

.. code-block:: python

  Application.serialization_format = "YamlFormat"

License
-------

This project is licensed under the MIT License - see the `LICENSE` file for details.
