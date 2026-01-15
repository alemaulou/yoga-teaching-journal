# Yoga Teaching Journal 🧘

A Streamlit app demonstrating Snowflake features for tracking yoga classes and getting AI-powered teaching suggestions.

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=flat&logo=snowflake&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

## Features

- **Log Classes** – Track date, location, theme, peak pose, student count, and vibe rating
- **Dashboard** – Visualize teaching patterns with Plotly charts
- **AI Inspiration** – Get personalized theme and sequence suggestions powered by Cortex AI
- **Class History** – Search and filter past classes with VARIANT data support

## Snowflake Concepts Demonstrated

| Feature | Concept |
|---------|---------|
| Normalized tables | Foreign keys, reference data |
| Flexible data | VARIANT column for JSON sequences |
| Analytics | Views for aggregated stats |
| AI Integration | Cortex AI_COMPLETE() function |

## The Core AI Pattern

```sql
-- CTE → LISTAGG → AI_COMPLETE()
WITH my_data AS (
    SELECT theme, AVG(student_count) AS avg_students
    FROM classes_taught
    GROUP BY theme
),
aggregated AS (
    SELECT LISTAGG(theme || ': ' || avg_students, '; ') AS context
    FROM my_data
)
SELECT AI_COMPLETE(
    model => 'mistral-large',
    prompt => 'Based on this data: ' || context || ' suggest a theme...'
) FROM aggregated;
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/yoga-teaching-journal.git
cd yoga-teaching-journal
```

### 2. Set up Snowflake database
```bash
pip install snowflake-snowpark-python
python setup_yoga_database.py
```
You'll be prompted for your Snowflake credentials.

### 3. Configure secrets
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials
```

### 4. Install dependencies and run
```bash
pip install -r requirements.txt
streamlit run yoga_teacher_streamlit_app.py
```

## Deploy to Streamlit Cloud

1. Push to GitHub (secrets.toml is gitignored)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in the Streamlit Cloud dashboard:
   - `account = "your-account"`
   - `user = "your-username"`
   - `password = "your-password"`

## File Structure

```
yoga-teaching-journal/
├── yoga_teacher_streamlit_app.py  # Main application
├── setup_yoga_database.py         # Database setup script
├── requirements.txt               # Python dependencies
├── .gitignore                     # Excludes secrets.toml
├── .streamlit/
│   └── secrets.toml.example       # Template for credentials
├── assets/
│   └── equinox_logo.png           # Logo image
└── README.md
```

## Author

**Alessandro Lou**  
Yoga Instructor at Equinox SF

---

*Built as a portfolio project to demonstrate Snowflake capabilities.*
