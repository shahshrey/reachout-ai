<div align="center">
  <a href="https://github.com/shahshrey/reachout-ai">
    <img src="https://github.com/shahshrey/reachout-ai/blob/master/assets/logo.webp" style="max-width: 500px" width="50%" alt="Logo">
  </a>
</div>

<div align="center">
  <em>An advanced AI-powered email generator designed to craft personalized and impactful cold outreach emails.</em>
</div>

<br />

<div align="center">
  <a href="https://github.com/shahshrey/reachout-ai/commits">
    <img src="https://img.shields.io/github/commit-activity/m/shahshrey/reachout-ai" alt="git commit activity">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?&color=3670A0" alt="License: MIT">
  </a>
</div>
<p align="center">
<a href="https://github.com/shahshrey/reachout-ai/tree/master">🖇️ Repository</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
</p>

<br/>

# ✉️ ReachOut AI

ReachOut AI is a sophisticated tool that leverages AI capabilities to generate personalized cold outreach emails. It integrates with Groq's language models to craft emails tailored to specific industries, roles, and purposes, ensuring high engagement and response rates.

## 🌟 Features

- 🤖 **AI-Powered Email Generation**: Utilizes Groq's LLaMA 3 model for creating highly personalized emails
- 📊 **User Registration**: Collects user information for personalized email creation
- 🎯 **Email Personalization**: Allows users to input recipient details and specific information
- 📄 **Document Upload**: Supports PDF upload for additional context in email generation
- ✉️ **Multiple Email Types**: Supports various email categories (e.g., Sales Pitch, Networking Introduction)
- 📝 **Email Preview and Editing**: Allows users to review and edit generated emails
- 📨 **Email Sending Functionality**: Integrated email sending capability
- 📊 **Performance Tracking**: Tracks email generation, sending, and response rates
- 🎨 **Custom UI**: Streamlit-based user interface with custom theming
- 🔒 **Secure Configuration**: Uses environment variables for sensitive information
- 📈 **CSV Data Storage**: Stores email data for analysis and tracking

## 🚀 Quick Start ⌨️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/reachout-ai.git
   cd reachout-ai
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Copy the `.env.example` file to `.env`
   - Fill in your API keys and other configuration values

5. Run the Streamlit app:
   ```bash
   streamlit run src/cold_email.py
   ```

6. Open your web browser and navigate to the URL provided by Streamlit (usually http://localhost:8501)

7. Follow the steps in the interface to register, personalize, generate, and send your emails.

## 🗂️ Project Structure

- `src/`: Contains the main application code
  - `cold_email.py`: The main application file
- `tests/`: Contains test files (to be implemented)
- `docs/`: Contains additional documentation
- `requirements.txt`: Lists all Python dependencies
- `.env.example`: Template for environment variables

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
