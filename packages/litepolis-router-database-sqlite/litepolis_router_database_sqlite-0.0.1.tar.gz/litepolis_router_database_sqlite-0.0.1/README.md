# LitePolis Router Database Example

This repository provides a working example of a database module for LitePolis, using SQLite as the database. It demonstrates how to create, read, update, and delete data using FastAPI and SQLModel.  You can use this example as a starting point to build your own custom database modules for LitePolis.

## Getting Started

Follow these steps to understand and adapt this example for your own LitePolis database module:

1. **Clone the Repository:** Clone this repository to your local machine.

2. **Install Dependencies:** Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Examine `setup.py`:** This file contains metadata about the example package.  When creating your own module, you'll need to change the following:
    * `name`: Change to your package's unique name (e.g., `litepolis-router-mydatabase`).
    * `version`, `description`, `author`, `url`: Update these fields accordingly.
    * `install_requires`: Add any additional dependencies your module requires.

4. **Understand the Core Logic (`litepolis_router_database_sqlite/core.py`):** This file sets up the FastAPI router and includes the routers for different data models (Users, Conversations, Comments).  The `init` function initializes the router, optionally taking a configuration object. The `DEFAULT_CONFIG` dictionary provides default configuration settings. When building your own module, you'll likely add more routers here for your specific data models.  The `prefix` variable is used to define the API endpoint prefix.

5. **Explore Data Models (`litepolis_router_database_sqlite/Users.py`, `Conversations.py`, `Comments.py`):** These files define the data models using SQLModel and implement the CRUD operations for each model.  Study these files to understand how to:
    * Define SQLModel classes for your tables.
    * Create FastAPI endpoints for each CRUD operation.
    * Use the `get_session` dependency for database interaction.
    * Handle errors and return appropriate responses.

6. **Adapt and Extend:**  Rename the entire `litepolis_router_database_sqlite` folder to your desired package name (e.g., `litepolis_router_mydatabase`).  Then, modify the files within this folder to implement your own database logic.  You'll need to:
    * Create new SQLModel classes for your tables.
    * Create corresponding FastAPI endpoints in separate files (like `Users.py`).
    * Include your new routers in the `core.py` file of your new package.
    * Update the tests in the `tests` folder to cover your new functionality.  Note that the `DEFAULT_CONFIG` and `init` function are crucial for the package manager to correctly initialize and start the services.

7. **Testing (`tests` folder):**  The `tests` folder contains example tests using `pytest`.  Examine `test_Users.py`, `test_Conversations.py`, and `test_Comments.py` to understand how to write tests for your database module.  When adapting this example, update these tests to reflect your changes and add new tests for your own data models and endpoints.  Run the tests using:
   ```bash
   pytest
   ```

8. Release your package to PyPI so that LitePolis package manager can automatically fetch the package during deployment.

9. Document the pre-requirements for deployment (e.g., Setup MySQL with `docker run -d MySQL` and edit the config first before serving the LitePolis system)

## Key Concepts and Hints

* **SQLModel:**  This library simplifies database interactions by mapping Python classes to database tables.  Learn more about SQLModel here: [https://sqlmodel.tiangolo.com/](https://sqlmodel.tiangolo.com/)

* **FastAPI:**  FastAPI is used to create the API endpoints.  Refer to the FastAPI documentation for details: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

* **Dependency Injection:**  The `get_session` dependency ensures that each endpoint has access to a database session.

* **Testing with Pytest:**  Pytest is used for writing and running tests.  See the pytest documentation for more information: [https://docs.pytest.org/en/7.1.x/](https://docs.pytest.org/en/7.1.x/)
