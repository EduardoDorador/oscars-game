# 🎬 Oscars 2025 Prediction Game

A simple Streamlit app where two people can predict Oscar winners and compete for a romantic dinner prize!

## 🚀 Quick Start (Local Testing)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run app.py
```

3. Open your browser at `http://localhost:8501`

## 📝 Configuration

Edit `config.json` to update:
- **lock_date**: Deadline for submissions (ISO format: "YYYY-MM-DDTHH:MM:SS")
- **oscars_date**: Date of the Oscars ceremony
- **categories**: Add/edit categories and nominees

Example:
```json
{
  "lock_date": "2025-03-02T20:00:00",
  "oscars_date": "2025-03-02",
  "categories": [
    {
      "id": "best_picture",
      "name": "Best Picture",
      "nominees": ["Movie 1", "Movie 2", "Movie 3"]
    }
  ]
}
```

## 🔐 Admin Panel

- Navigate to "Admin Panel" in the sidebar
- Default password: `oscars2025` (change this in `app.py` line 110!)
- Enter the actual Oscar winners after the ceremony

## 🌐 Deployment to Streamlit Cloud (FREE)

1. Create a GitHub repo and push this code
2. Go to https://share.streamlit.io/
3. Sign in with GitHub
4. Click "New app"
5. Select your repo, branch, and `app.py`
6. Click "Deploy"!
7. Share the URL with your girlfriend

## 📱 How It Works

1. **Before Oscars**: Both users visit the URL and submit their predictions
2. **Lock Date**: Submissions automatically lock at the configured date/time
3. **After Oscars**: Admin enters the actual winners
4. **Results**: App automatically calculates scores and declares the winner!

## 🗄️ Database

Uses SQLite (`oscars_predictions.db`) which persists between restarts. The database is automatically created on first run.

## 🎯 Features

- ✅ Simple name-based identification (no passwords needed)
- ✅ Can update predictions before deadline
- ✅ Automatic locking based on date
- ✅ Admin panel for entering winners
- ✅ Automatic score calculation
- ✅ Detailed comparison view
- ✅ Mobile-friendly

## 💡 Tips

- Test locally first before deploying
- Update the admin password in `app.py`
- The lock date is in your local timezone
- You can edit predictions until the lock date
- The database file will persist on Streamlit Cloud

Enjoy your romantic Oscar prediction game! 🏆❤️
