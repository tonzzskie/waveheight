# Wave Height Flask App

The **Wave Height Flask App** is a web application designed to track and display wave height data. Built with Flask, this app aims to provide users with real-time wave height insights, with future plans for implementing user authentication, an admin dashboard, and a fully functional database.

## Features

- **Real-time Wave Height Tracking**: Displays the latest wave height data in a user-friendly interface.
- **Scalable Architecture**: Designed to be easily expanded with additional data sources and functionalities.
- **User Authentication** (Upcoming): Plan to include login, signup, and administrative privileges for data management.
- **Database Integration** (Upcoming): Future support for a database to store and retrieve wave height records.

## Installation

To set up and run the application locally, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone git@github.com:tonzzskie/waveheight.git
   cd waveheight
   ```

2. **Set Up the Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   Ensure you have `pip` installed, then install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python run.py
   ```

   The app should be accessible at `http://127.0.0.1:5000`.

## Project Structure

```
waveheight/
├── config.py               # Configuration file
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point for the Flask app
├── venv/                   # Virtual environment (ignored by Git)
└── wave_height/            # Application source code (models, views, etc.)
```

## Future Enhancements

- **Database Integration**: To store and manage wave data.
- **User Authentication**: Login/signup with admin privileges.
- **API Integration**: Support for external data sources.
- **Data Visualization**: Improved charting for wave height trends.

## Contributing

If you’d like to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`.
3. Make your changes and commit: `git commit -m 'Add some feature'`.
4. Push to your branch: `git push origin feature-branch`.
5. Submit a pull request.

## License

This project is licensed under the MIT License.

---
