=======================================================
Knowledge Informatics Unique Identifier Generator Utils
=======================================================

Collection of Python modules for generating unique identifiers.


Installation
------------

.. code-block:: shell

    pip install kis-uid-generator-utils

Usage
-----
Example Python script:

.. code-block:: python

    from kis_uid_generator_utils import constants
    from kis_uid_generator_utils.generator import Generator

    config_file = constants.DEFAULT_CONFIG_FILE

    # Example usage
    if __name__ == "__main__":
        generator = Generator(config_file=config_file)

        # Generate some example IDs
        print(generator.generate_id("gene"))  # e.g., "GN-5f8b3a2e-20250304"
        print(generator.generate_id("protein", "BRCA1"))  # e.g., "PR-BRCA1-7a9c2d1f-20250304"
        print(generator.generate_id("variant"))  # e.g., "VR-8b3e4f5a-20250304"

Invocation:

.. code-block:: shell

    python example.py
    GN-192f63b6-20250305
    PR-BRCA1-0ed3e01b-20250305
    VR-6e2bf02e-20250305
