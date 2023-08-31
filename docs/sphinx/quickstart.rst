Quickstart
===============================

View the Live application
-------------------------

The best way to get started with the application is by visiting the application hosted in streamlit community cloud `here <https://ai-chatverse.streamlit.app/>`_.

**Note:** LLAMA2 uses llama cpp and needs a aritifact, it can only be run locally.

PS: Please configure the installation according to this `Link <https://python.langchain.com/docs/integrations/llms/llamacpp>`_.

Running from docker locally via official docker image
-----------------------------------------------------

The application can be run locally using docker by running the following command

.. code-block:: console
   
   
   docker run --rm -it -p 8501:8501 pevatrons/ai-chatverse


Running the latest version of the app from source in docker
-----------------------------------------------------------
#. Clone the `repository <https://github.com/scmpevatrons/ai-chatverse>`_
#. Build the image by running
   
   .. code-block:: console
      
      docker build -t ai_chaverse .

#. Run the application by
    
   .. code-block:: console

      docker run --rm -it -p 8501:8501 ai_chaverse

#. Visit `localhost:8501 <http://localhost:8501/>`_

