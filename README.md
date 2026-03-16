1. Open **MySQL Workbench**.
2. Run the **SQL schema script** provided in the project.
3. This script will automatically create **three databases**:

   * `CIDER_HR`
   * `CIDER_CRIME`
   * `CIDER_EVIDENCE`
4. It will also insert the **dummy (sample) data** needed for the project.

---

### Step 2: Install the Required Python Packages

Open the **terminal inside the project folder** and run the following command:

`pip install -r requirements.txt`

This will install:

* **Streamlit** (for the dashboard)
* **MySQL connectors** (so Python can talk to the database)

---

### Step 3: Set Up Your Database Password (VERY IMPORTANT)

Do **not** write your database password directly inside the Python files.

1. In the **main project folder**, create a new file named **`.env`**
   *(Make sure the file name starts with a dot.)*

2. Add the following lines inside the file:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_password_here
```

3. Replace `your_actual_password_here` with **your real MySQL password**.

**Note:** The `.gitignore` file makes sure this `.env` file is **not uploaded to GitHub**, so your password stays private.

---

### Step 4: Run the Application

After:

* the database is running, and
* the `.env` file is created,

open the terminal and run:

`streamlit run app.py`

Your **web browser will open automatically**, showing the working **dashboard application**.
