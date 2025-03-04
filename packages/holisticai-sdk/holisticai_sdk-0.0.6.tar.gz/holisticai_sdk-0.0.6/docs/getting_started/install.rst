============
Installation
============

`holisticai-sdk` is avaiable on Azure Artifacts. You can install the library with `pip` using the following command:

.. code-block::

  # Install keyring to store credentials
  pip install keyring artifacts-keyring

  # Run assessments in a self-contained environment
  pip install --extra-index-url https://{access_token}@pkgs.dev.azure.com/holisticai/holisticai-sdk/_packaging/holisticai-sdk/pypi/simple holisticai-sdk
  
  # Run assessments in your local environment
  pip install haisdk[full] 

.. toctree::
    :maxdepth: 2
    :titlesonly:

    install