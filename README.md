# Flask Text Scraping and Analysis Application

This is a Flask-based web application designed for text scraping and analysis. It features user authentication via email OTP, GitHub, and Google, along with an admin panel to view the history of processed articles. The application scrapes text from given URLs, analyzes the content, and provides insights into the writing style and word usage.

## Features

- **Text Scraping**: Extracts text from a given URL using the `newspaper` library.
- **Text Analysis**: Analyzes the text for sentence and word count, POS tagging, keyword extraction, and stop words count using NLTK.
- **Writing Style Analysis**: Determines the writing style based on adjective/pronoun and adverb/adjective ratios.
- **Admin Panel**: View history of processed articles with detailed analysis, accessible via email OTP, GitHub, or Google login.
- **Visualizations**: Generates and displays a bar graph of POS ratios.
- **Email OTP Authentication**: Secure login for admins using email OTP.
- **GitHub and Google OAuth**: Allows login via GitHub and Google for admin access.

## Prerequisites

- Python 3.7+
- PostgreSQL
- Required Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/flask-text-scraping.git
   cd flask-text-scraping
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data:**
   ```python
   import nltk
   nltk.download('averaged_perceptron_tagger')
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('universal_tagset')
   ```

5. **Set up PostgreSQL database:**
   - Create a new PostgreSQL database.
   - Update the database configuration in the code (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`).

6. **Create the database table:**
   ```python
   from your_flask_app import create_table
   create_table()
   ```

7. **Configure OAuth credentials:**
   - **GitHub OAuth:**
     - Register your application on GitHub to get the `CLIENT_ID` and `CLIENT_SECRET`.
     - Update the values in the code.
   - **Google OAuth:**
     - Follow [Google's instructions](https://developers.google.com/identity/protocols/oauth2) to create OAuth credentials.
     - Save the `client_secret.json` file in the project directory.

8. **Configure email settings for OTP:**
   - Update the Flask-Mail configuration with your Gmail credentials.
   - Allow less secure apps access to your Gmail account or use an App Password.

## Running the Application

1. **Run the Flask application:**
   ```bash
   python your_flask_app.py
   ```

2. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- **Home Page**: Enter the URL of the article to be scraped and analyzed.
- **Admin Login**: Login using email OTP, GitHub, or Google to access the admin panel and view the history of processed articles.

## Admin Access

- **Email OTP**: Enter your email and OTP sent to your registered email to login.
- **GitHub Login**: Use your GitHub credentials to login. Ensure your GitHub username is listed in `github_admin_usernames`.
- **Google Login**: Use your Google account to login. Ensure your Google email is listed in `admin_emails`.

## Files

- `your_flask_app.py`: Main application code.
- `templates/`: HTML templates for rendering web pages.
- `static/`: Static files (CSS, JS, images).
- `client_secret.json`: Google OAuth client secret file (not included, generate and add your own).

## Security Considerations

- Keep your secret keys and OAuth credentials secure.
- Use environment variables for sensitive configurations in a production environment.
- Consider using a more secure email setup for Flask-Mail in production.


## Contact

For any questions or suggestions, please contact `saneeipk@gmail.com`.

---

Replace `your_flask_app` with the actual name of your Flask application file. Make sure to adjust any specific configurations and paths based on your actual setup.
