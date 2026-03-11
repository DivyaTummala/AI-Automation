# WinETL - Enterprise ETL Configuration Interface

## 🚀 Quick Start

### Running the Web Application

1. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Web Server**:
   ```bash
   python app.py
   ```

3. **Access the Application**:
   - Open your browser and navigate to:
     - **http://localhost:5000**
     - OR **http://127.0.0.1:5000**

### Running the Desktop Application (Tkinter)

```bash
python main.py
```

## 📋 Features

### Web Interface (Recommended)
- Modern, responsive design
- Accessible via any web browser
- Beautiful gradient UI matching the reference design
- No hardcoded values - all fields are empty by default
- Real-time configuration saving

### Desktop Interface (Alternative)
- Native Windows application using Tkinter
- Standalone desktop experience

## 🎯 Application URLs

**Web Application:**
- Local URL: `http://localhost:5000`
- Network URL: `http://127.0.0.1:5000`
- If running on a network: `http://<your-ip-address>:5000`

## 📝 Configuration

### Source Configuration Fields:
- Source Type (RDBMS, File, API)
- Source Database Type (SQL Server, MySQL, PostgreSQL, Oracle, MongoDB)
- Server/Host
- Database Name
- Port
- Authentication Type
- Username
- Password

### Target Configuration Fields:
- Target Type (Flat File, RDBMS, Data Platform/Lakehouse)
- Target Location/Path
- Target Format (CSV, JSON, Parquet, Excel)

## 🔧 Project Structure

```
Divya Automation/
├── app.py                  # Flask web application
├── main.py                 # Tkinter desktop application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web UI template
└── README.md              # This file
```

## 💡 Usage

1. **Configure Source**: Fill in your database connection details in the left panel
2. **Configure Target**: Select your target type and destination in the right panel
3. **Test Connection**: Click "Test Connection" to validate your settings
4. **Save**: Configuration is automatically saved when you test the connection

## 🛠️ Technology Stack

- **Backend**: Flask 3.0.0, Python
- **Frontend**: HTML5, CSS3, JavaScript
- **Desktop**: Tkinter
- **Future**: FastAPI integration planned

## 📞 Support

For issues or questions, please check the console output or error logs.

---
*WinETL Infinity - Enterprise ETL Validation & Data Reconciliation Engine © 2026*

