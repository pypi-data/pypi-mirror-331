Fronts File
===========

The `Saes` library provides a multiobjective module designed for data from multiobjective optimization studies. If you need to generate Pareto front plots from your data, you must configure two data sources:

Configuring Algorithm Fronts
----------------------------

Each algorithm's front data should be organized in the following folder structure:

.. code-block::

    📂 fronts_folder  
    ├── 📂 algorithm-1/            
    │   ├── 📂 instance-1  
    |   |    ├── BEST_metric-1_FUN.csv
    |   |    ├── MEDIAN_metric-1_FUN.csv
    |   |    .
    |   |    .
    |   |    ├── BEST_metric-k_FUN.csv
    |   |    ├── MEDIAN_metric-k_FUN.csv
    │   ├── 📂 instance-2
    |   .
    |   .
    |   └── 📂 instance-m
    ├── 📂 algorithm-2/             
    .
    .
    ├── 📂 algorithm-n/               

Structure Details
-----------------

- Each **algorithm** has its own directory inside ``fronts_folder``.  
- Within each algorithm’s folder, **instances** are stored as subdirectories.  
- Each instance contains multiple CSV files representing Pareto fronts, following the format:  
  
  - ``BEST_metric-x_FUN.csv``: The best Pareto front based on metric `x`.  
  - ``MEDIAN_metric-x_FUN.csv``: The median Pareto front based on metric `x`.  

