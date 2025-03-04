.. SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
..
.. SPDX-License-Identifier: CC-BY-4.0

.. start-badges

|python-versions| |pypi| |license| |reuse-status| |rtd-status| |pipeline-status|

.. |pypi| image:: https://img.shields.io/pypi/v/axonometry?label=PyPI&logo=pypi&color=blue
   :target: https://pypi.org/project/axonometry/

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/axonometry.svg
   :target: https://pypi.org/project/axonometry/

.. |license| image:: https://img.shields.io/pypi/l/axonometry?color=blue
   :target: https://axonometry.readthedocs.io/en/latest/license.html

.. |reuse-status| image:: https://api.reuse.software/badge/codeberg.org/mononym/axonometry
   :target: https://api.reuse.software/info/codeberg.org/mononym/axonometry

.. |rtd-status| image:: https://img.shields.io/readthedocs/axonometry?label=Read%20the%20Docs&logo=read-the-docs
   :target: https://axonometry.readthedocs.io/en/latest/

.. |pipeline-status| image:: https://ci.codeberg.org/api/badges/14144/status.svg?branch=beta
   :target: https://ci.codeberg.org/repos/14144/branches/beta

.. end-badges

Contents
^^^^^^^^

- `What is axonometry? <#what-is-axonometry>`__
- `How does it work? <#how-does-it-work>`__
- `Examples <#examples>`__
- `Installation <#installation>`__
- `Contributing <#contributing>`__
- `Acknowledgement <#acknowledgement>`__
- `License <#license>`__

.. start-pitch

What is axonometry?
-------------------

*axonometry* is a scripting library for generating axonometric drawings. It implements axonometric projection operations commonly used in the context of architectural representation. *axonometry* allows the exploration of three dimensional representation through the definition of projection operations. Think of it as a tool for generative drawing, oriented towards architectural representation.

*axonometry* is the tip of the iceberg of a PhD project at the `AlICe laboratory <https://alicelab.be>`__. It is the result of a practical experimentation around questions related to the field of architectural representation, the role of computer graphics and drawing practices.

How does it work?
-----------------

*axonometry* is basically a wrapper for `compas <https://compas.dev>`__ geometry objects and produces SVG vector files with the help of `vpype <https://vpype.readthedocs.io>`__.

Examples
--------

You don’t like computers and just want an axonometry layout and continue drawing by hand:

.. code:: python

   import axonometry as axo
   my_axo = axo.Axonometry(15,45)
   my_axo.save_svg("new_drawing")

Installation
------------

Please refer to the `install section <https://axonometry.readthedocs.io/en/latest/install.html>`__ for detailed installation instructions and recommendations.

TL;DR:

- Python 3.12 is recommended, but *axonometry* is also compatible with Python 3.10 and 3.11.
- *axonometry* is published on the `Python Package Index <https://pypi.org/project/axonometry/>`__.

.. code:: bash

   python -m pip install axonometry

Contributing
------------

All type of feedback is welcome. Contributions can take any form and do not necessarily require software development skills! Check the `Contributing section <https://axonometry.readthedocs.io/en/latest/contributing.html>`__ for more information.

Acknowledgement
---------------

Many thanks to the developers of *compas* and *vpype*. Not only did their libraries make this project possible, but inspecting their elegant codebase was an invaluable resource for deepening my Pyhton knowledge.

License
-------

This project is licensed under the GPLv3 License. Check the `Liceneses section <https://axonometry.readthedocs.io/en/latest/license.html>`__ for more information.

.. end-pitch
