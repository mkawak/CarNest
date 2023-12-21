# CarNest

## Description
CarNest, a car listings website, was created as part of the Entrepreneurship in Computing course at the University of California, Riverside (CS175). This web application leverages Flask, a powerful and lightweight web framework, for its backend operations and uses traditional HTML templating for an engaging and user-friendly front-end experience. CarNest stands out by offering users a seamless platform to browse, list, and manage car listings, coupled with an integrated administrative panel for enhanced oversight and control.

### Key Features

- **User-Friendly Listing Browsing**: Users can easily navigate and explore a wide range of car listings.
- **Efficient Listing Management**: Sellers can list their cars with ease, providing detailed information and images.
- **Integrated Administrative Panel**: An intuitive administrative interface embedded within the user interface allows for the review, approval, denial, or deletion of listings, ensuring quality and reliability.
- **Seamless MongoDB Integration**: Utilizing MongoDB for data storage, CarNest offers robust and scalable database solutions.
- **Responsive Front-End Design**: Crafted with traditional HTML and modern design principles, the front-end ensures a responsive and accessible user experience.

## Technologies Used
- Flask
- MongoDB
- HTML/CSS

## Installation
### 1. Clone the Repository

- [CarNest](https://github.com/mkawak/CarNest.git)

### 2. Configure a Local Python Interpreter

To run this application, you'll need Python 3.12. If you haven't installed Python 3.12 yet, you can download it from the [official Python website](https://www.python.org/downloads/). Once Python is installed, follow these steps to configure your local environment:

- **Verify Python Installation**:
  - Open a terminal or command prompt.
  - Check your Python version by running:
    ```
    python --version
    ```
    Make sure it says Python 3.12 or later.

- **Create a Virtual Environment**:
  - It's recommended to use a virtual environment to manage dependencies.
  - In the root directory of your project, create a new virtual environment:
    - For macOS/Unix:
      ```
      python3 -m venv venv
      ```
    - For Windows:
      ```
      python -m venv venv
      ```
  - This creates a new folder `venv` in your project directory, containing the virtual environment.

- **Activate the Virtual Environment**:
  - Before installing dependencies, activate the virtual environment:
    - For macOS/Unix:
      ```
      source venv/bin/activate
      ```
    - For Windows:
      ```
      venv\Scripts\activate
      ```

### 3. Install Dependencies

- **Install Requirements**:
  - Ensure that you are in the project's root directory.
  - For macOS/Unix and Windows:
    ```
    pip install -r requirements.txt
    ```
    
### 4. Configuration Instructions

### Setting up MongoDB

To ensure the smooth operation of the server, it's necessary to configure the MongoDB paths correctly. Please follow these steps:

1. **Modifying `server.py`**:
   - Navigate to `server.py`.
   - Locate and modify line 14 to point to your `start_mongodb.sh` script. 
     For example:
     ```python
     subprocess.Popen(["<YourPath>/start_mongodb.sh"])
     ```
   - Similarly, adjust line 19 to match your MongoDB URI.
     For example:
     ```python
     app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
     ```

2. **Configuring `start_mongodb.sh`**:
   - Open `start_mongodb.sh`.
   - Modify the script to include the correct path to your database.
     For example:
     ```bash
     #!/bin/bash
     mongod --dbpath <YourPath>/db
     ```
   - Ensure that the `start_mongodb.sh` script is executable. You can achieve this by running:
     ```
     chmod +x start_mongodb.sh
     ```

These steps are crucial for connecting to the MongoDB database correctly and ensuring that the server operates as expected. Ensure that the paths are set according to your local setup.



## Author
- Majd Kawak
