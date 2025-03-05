==============
eLoRA
==============

eLoRA: Efficient Low-Rank Allocation for Budget-Constrained Fine-Tuning 🧮💰⚙️🎛️


Installation
------------

To install the package, use pip:

.. code-block:: bash

    pip install elora


Usage
-----

To use the package, import it in your Python code:

.. code-block:: python

  import elora


    ranks = elora.rank_pattern(
            model="meta-llama/Llama-3.2-1B",
            base_rank=16,
            # target_modules="all",
            target_modules=["q_proj", "down_proj"],
            # layers="all",
            layers=[2, 3]
        )



Models.

.. code-block:: python

    import elora

    # Under development


GitHub repository: https://github.com/mohsenhariri/eLoRA
