import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "oscars_predictions.db"

def init_db():
    """Initialize database with predictions and winners tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            category_id TEXT NOT NULL,
            prediction TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_name, category_id)
        )
    """)
    
    # Winners table (for actual Oscar results)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS winners (
            category_id TEXT PRIMARY KEY,
            winner TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_predictions(user_name: str, predictions: Dict[str, str]):
    """Save or update user predictions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for category_id, prediction in predictions.items():
        cursor.execute("""
            INSERT INTO predictions (user_name, category_id, prediction)
            VALUES (?, ?, ?)
            ON CONFLICT(user_name, category_id) 
            DO UPDATE SET prediction=?, submitted_at=CURRENT_TIMESTAMP
        """, (user_name, category_id, prediction, prediction))
    
    conn.commit()
    conn.close()

def get_user_predictions(user_name: str) -> Dict[str, str]:
    """Get all predictions for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT category_id, prediction 
        FROM predictions 
        WHERE user_name = ?
    """, (user_name,))
    
    predictions = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return predictions

def has_submitted(user_name: str) -> bool:
    """Check if user has already submitted predictions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM predictions WHERE user_name = ?
    """, (user_name,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def save_winners(winners: Dict[str, str]):
    """Save actual Oscar winners"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for category_id, winner in winners.items():
        cursor.execute("""
            INSERT INTO winners (category_id, winner)
            VALUES (?, ?)
            ON CONFLICT(category_id) 
            DO UPDATE SET winner=?, updated_at=CURRENT_TIMESTAMP
        """, (category_id, winner, winner))
    
    conn.commit()
    conn.close()

def get_winners() -> Dict[str, str]:
    """Get all saved winners"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT category_id, winner FROM winners")
    winners = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return winners

def get_all_predictions() -> List[Dict]:
    """Get all predictions from all users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_name, category_id, prediction, submitted_at
        FROM predictions
        ORDER BY user_name, category_id
    """)
    
    predictions = []
    for row in cursor.fetchall():
        predictions.append({
            "user_name": row[0],
            "category_id": row[1],
            "prediction": row[2],
            "submitted_at": row[3]
        })
    
    conn.close()
    return predictions

def calculate_scores() -> Dict[str, int]:
    """Calculate scores for all users based on saved winners"""
    winners = get_winners()
    if not winners:
        return {}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT user_name FROM predictions")
    users = [row[0] for row in cursor.fetchall()]
    
    scores = {}
    for user in users:
        cursor.execute("""
            SELECT category_id, prediction
            FROM predictions
            WHERE user_name = ?
        """, (user,))
        
        user_predictions = cursor.fetchall()
        correct = sum(1 for cat_id, pred in user_predictions 
                     if winners.get(cat_id) == pred)
        scores[user] = correct
    
    conn.close()
    return scores

def delete_user_predictions(user_name: str):
    """Delete all predictions for a specific user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM predictions WHERE user_name = ?", (user_name,))
    
    conn.commit()
    conn.close()

def get_all_users_with_dates() -> List[Dict]:
    """Get all users who submitted predictions with their submission dates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_name, MAX(submitted_at) as last_updated
        FROM predictions
        GROUP BY user_name
        ORDER BY last_updated DESC
    """)
    
    users = []
    for row in cursor.fetchall():
        users.append({
            "user_name": row[0],
            "last_updated": row[1]
        })
    
    conn.close()
    return users