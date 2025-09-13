**📦 TNS Staff Access Dashboard**
A modular, audit-friendly reservation and engagement dashboard built with Streamlit, Google Sheets, and TOML-based secrets management. Designed for transparency, traceability, and intuitive workflows across event logistics, campaign coordination, and participant engagement.

**🚀 Features**
- 🔐 Google-authenticated access with role-based controls
- 📅 Reservation management with contextual UI and inline editing
- 📊 PAX distribution charts and daily summaries
- 🧾 Audit trail with UUIDs and timestamped logging
- 📁 Config-driven deployment using nested TOML secrets
- 📈 Dashboard filters by date, contact, and status
- 🧠 Status taxonomy includes: In-Progress, Confirmed, Cancelled, Completed, Lost
- 🧬 Extensible architecture for future modules (e.g., sponsorship tracking, feedback collection)

**🛠️ Tech Stack**
Frontend 		- 	Streamlit
Auth			-	Google OAuth via Streamlit integration
Backend			-	Google Sheets API via gspread
Config			-	TOML + environment variables
Logging			-	Custom Google Sheet logger
Visualization	-	Plotly Express

**📁 Folder Structure**
```
tns_staff_access/
├── .streamlit/           # Config and secrets
├── config/               # Sheet adapter, logger, auth
├── pages/                # Multi-page Streamlit modules
│   ├── 1_Dashboard.py
│   ├── 2_Manage_Reservations.py
│   └── ...
├── utils/                # Reusable helpers
├── .gitignore
├── README.md
└── requirements.txt
```

**⚙️ Setup Instructions**
**- Clone the repo**
git clone https://github.com/your-username/tns_staff_access.git
**cd tns_staff_access**
- Create virtual environment
**python -m venv .venv**
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
**- Install dependencies**
pip install -r requirements.txt
**- Configure secrets**
Add your Google credentials and sheet IDs to .streamlit/secrets.toml
**- Run the app**
streamlit run Home.py

**✅ Best Practices**
- Use audit_trail_id for all record updates
- Avoid hardcoding sheet names—use config/sheet_adapter.py
- Validate all inputs before submission
- Use sanitize_for_json() before updating sheets to avoid serialization errors

**📌 Roadmap**
- [x] Reservation dashboard with inline editing
- [x] PAX summary and pie chart visualization
- [ ] Sponsorship tracking module
- [ ] Feedback collection and sentiment analysis
- [ ] Multilingual support for participant communication

**🤝 Contributing**
Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

**📜 License**
MIT License. See LICENSE file for details.

