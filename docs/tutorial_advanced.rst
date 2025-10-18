Tutorial Advanced: Optimization and Best Practices
==================================================

🎯 Goals
--------

By the end of this tutorial, you'll be able to:

* Identify performance bottlenecks and optimize Python code in PyArchInit-Mini
* Apply architectural and coding best practices for scalable CLI applications
* Profile, refactor, and test code for efficiency and maintainability
* Avoid common pitfalls that can lead to slow or buggy behavior

📋 Prerequisites
----------------

Before starting, you should:

* Be comfortable with Python (functions, classes, modules)
* Know basic command-line usage
* Have PyArchInit-Mini installed:

  .. code-block:: bash

     pip install pyarchinit-mini

* (Optional) Have a sample archaeological dataset for experiments

📖 Key Concepts
---------------

Let's clarify the important ideas we'll build upon:

* **Profiling**: Measuring where your code spends time or uses resources.
* **Refactoring**: Improving code without changing its external behavior.
* **Best Practices**: Rules and conventions that make code faster, safer, or easier to maintain.
* **Bottlenecks**: Parts of code or architecture that limit performance.
* **CLI Optimization**: Making command-line interfaces fast and responsive, especially with large data.

💻 Practical Example
--------------------

We're going to optimize a common PyArchInit-Mini task: **listing and filtering archaeological finds**.

Suppose you want to quickly list all artifacts from a given period, and you notice the operation is slow with large datasets. We'll profile, optimize, and refactor this functionality.

Step 1: Profiling a Slow Listing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's simulate a "slow" function that retrieves all artifacts from the database and filters them in Python.

.. code-block:: python

   import time

   # Simulated artifact data (Mimicking a big dataset)
   artifacts = [
       {"id": i, "name": f"Artifact_{i}", "period": "Roman" if i % 3 == 0 else "Medieval"}
       for i in range(100000)
   ]

   def list_artifacts_by_period(period):
       results = []
       for artifact in artifacts:
           if artifact["period"] == period:
               results.append(artifact)
       return results

   start = time.time()
   roman_artifacts = list_artifacts_by_period("Roman")
   end = time.time()

   print(f"Found {len(roman_artifacts)} artifacts in {end - start:.3f} seconds.")

**Output**:

.. code-block::

   Found 33334 artifacts in 0.055 seconds.

**Explanation**:  
This approach works, but as your dataset grows, filtering in Python becomes inefficient. If your data is in a database, filtering there is *much* faster.

Step 2: Optimize with List Comprehension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python's list comprehensions are faster than explicit loops for filtering.

.. code-block:: python

   start = time.time()
   roman_artifacts = [a for a in artifacts if a["period"] == "Roman"]
   end = time.time()

   print(f"Found {len(roman_artifacts)} artifacts in {end - start:.3f} seconds.")

**Output**:

.. code-block::

   Found 33334 artifacts in 0.027 seconds.

**Explanation**:  
A simple rewrite halves the time! But let's do better by *not* loading everything into memory.

Step 3: Database-Level Filtering (Best Practice)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In real PyArchInit-Mini usage, data lives in a database. Always filter with SQL, not Python.

Suppose you have a `finds` table with a `period` column.

.. code-block:: python

   import sqlite3

   # Connect to a demo SQLite database
   conn = sqlite3.connect(":memory:")
   c = conn.cursor()
   c.execute("CREATE TABLE finds (id INTEGER, name TEXT, period TEXT)")
   c.executemany(
       "INSERT INTO finds VALUES (?, ?, ?)",
       [(i, f"Artifact_{i}", "Roman" if i % 3 == 0 else "Medieval") for i in range(100000)]
   )

   start = time.time()
   c.execute("SELECT id, name, period FROM finds WHERE period = ?", ("Roman",))
   roman_artifacts = c.fetchall()
   end = time.time()

   print(f"Found {len(roman_artifacts)} artifacts in {end - start:.3f} seconds.")

**Output**:

.. code-block::

   Found 33334 artifacts in 0.010 seconds.

**Explanation**:  
Let your database do the filtering! It's dramatically faster and uses less memory.

Step 4: Refactoring for Reuse and Maintainability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's wrap the optimized pattern into a reusable, well-documented function.

.. code-block:: python

   def get_artifacts_by_period(conn, period):
       """
       Efficiently retrieve artifacts from the database by period.
       Args:
           conn: sqlite3.Connection
           period: str
       Returns:
           List of (id, name, period) tuples
       """
       with conn:  # Context management ensures resource safety
           cur = conn.execute(
               "SELECT id, name, period FROM finds WHERE period = ?",
               (period,)
           )
           return cur.fetchall()

   # Usage
   start = time.time()
   roman_artifacts = get_artifacts_by_period(conn, "Roman")
   end = time.time()
   print(f"Found {len(roman_artifacts)} artifacts in {end - start:.3f} seconds.")

**Output**:

.. code-block::

   Found 33334 artifacts in 0.010 seconds.

**Explanation**:  
Clear, concise, DRY (Don't Repeat Yourself), and much easier to test!

🎓 Exercises
------------

1. **Exercise:**  
   Refactor the following code to use a generator expression so it uses less memory.  
   .. code-block:: python

      def medieval_artifact_names(artifacts):
          names = []
          for a in artifacts:
              if a["period"] == "Medieval":
                  names.append(a["name"])
          return names

   **Solution:**  
   .. code-block:: python

      def medieval_artifact_names(artifacts):
          return (a["name"] for a in artifacts if a["period"] == "Medieval")

   # Usage
   gen = medieval_artifact_names(artifacts)
   print(next(gen))  # Output: Artifact_1

2. **Exercise:**  
   Suppose you see a slow query in your CLI. How would you profile where the bottleneck is in your code?

   **Solution:**  
   Use Python's built-in cProfile module:
   .. code-block:: python

      import cProfile
      cProfile.run("list_artifacts_by_period('Roman')")

   Or for more readable output:

   .. code-block:: python

      import timeit
      print(timeit.timeit("list_artifacts_by_period('Roman')", globals=globals(), number=1))

💡 Tips
-------

* Always filter/sort data in your database, not in Python, for large datasets.
* Profile before you optimize—don't "guess" where the slowness is!
* Use list comprehensions and generator expressions for memory and speed.
* Use context managers (with statements) to manage resources safely.
* Document every function: what it does, its arguments, and return values.
* Write small, single-purpose functions; they're easier to test and optimize.

⚠️ Common Errors
---------------

* Filtering or processing huge datasets in Python memory instead of querying the database efficiently.
* Not using indexes in your database—make sure columns you filter on are indexed!
* Mixing business logic with database code—keep them separate for testability.
* Forgetting to close database connections (use `with` or always call `conn.close()`).
* Over-optimizing before measuring—always profile first.

🔗 Additional Resources
----------------------

* `Python cProfile and profiling <https://docs.python.org/3/library/profile.html>`_
* `PEP 8: Python Style Guide <https://peps.python.org/pep-0008/>`_
* `sqlite3 Python Docs <https://docs.python.org/3/library/sqlite3.html>`_
* `PyArchInit-Mini Source & Issues <https://github.com/your-org/pyarchinit-mini>`_
* `Effective Python: 90 Specific Ways to Write Better Python <https://effectivepython.com/>`_

---

**Congratulations!**  
You've learned how to identify and optimize slow code, leverage best practices, and keep your archaeological CLI apps fast and maintainable. Keep profiling, and happy coding!