import streamlit as st
import json
from datetime import datetime
import database as db

# Page config
st.set_page_config(
    page_title="Oscars 2025 Prediction Game 🎬",
    page_icon="🏆",
    layout="centered"
)

# Initialize database
db.init_db()

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

def is_locked() -> bool:
    """Check if submissions are locked based on config date"""
    lock_date = datetime.fromisoformat(config["lock_date"])
    return datetime.now() >= lock_date

def show_prediction_form():
    """Show the prediction form for users"""
    st.title("🎬 Oscars 2025 Prediction Game")
    st.markdown("### Pick your winners! 🏆")
    
    # Check if locked
    if is_locked():
        st.error(f"⏰ Submissions are locked! The deadline was {config['lock_date']}")
        st.info("Check the Results tab to see how you did!")
        return
    
    # User name input
    user_name = st.text_input("Your Name:", placeholder="Enter your name").strip()
    
    if not user_name:
        st.info("👆 Enter your name to start predicting!")
        return
    
    # Check if already submitted
    has_previous = db.has_submitted(user_name)
    previous_predictions = db.get_user_predictions(user_name) if has_previous else {}
    
    if has_previous:
        st.warning(f"⚠️ You already submitted predictions! You can update them below.")
    
    # Prediction form
    st.markdown("---")
    predictions = {}
    
    for category in config["categories"]:
        st.subheader(f"🎭 {category['name']}")
        
        # Get previous selection if exists
        previous = previous_predictions.get(category["id"])
        default_index = 0
        if previous and previous in category["nominees"]:
            default_index = category["nominees"].index(previous)
        
        prediction = st.selectbox(
            f"Who will win {category['name']}?",
            options=category["nominees"],
            key=category["id"],
            index=default_index
        )
        predictions[category["id"]] = prediction
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Submit Predictions", type="primary", use_container_width=True):
            db.save_predictions(user_name, predictions)
            st.success(f"✅ Predictions saved for {user_name}!")
            st.balloons()
            st.info("You can come back and update your predictions anytime before the deadline!")

def show_admin_panel():
    """Admin panel to enter actual Oscar winners"""
    st.title("🔐 Admin Panel")
    
    # Simple password protection
    admin_password = st.text_input("Admin Password:", type="password")
    
    if admin_password != "oscars2025":  # Change this password!
        if admin_password:
            st.error("❌ Wrong password!")
        return
    
    st.success("✅ Admin access granted!")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["👥 Manage Users", "📋 View Predictions", "🏆 Enter Winners"])
    
    with tab1:
        st.markdown("### All Submissions")
        
        users = db.get_all_users_with_dates()
        
        if not users:
            st.info("📭 No predictions submitted yet!")
        else:
            st.write(f"**Total users:** {len(users)}")
            st.markdown("---")
            
            for user_data in users:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**👤 {user_data['user_name']}**")
                
                with col2:
                    st.caption(f"📅 {user_data['last_updated']}")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{user_data['user_name']}", type="secondary"):
                        db.delete_user_predictions(user_data['user_name'])
                        st.success(f"Deleted {user_data['user_name']}'s predictions!")
                        st.rerun()
                
                st.markdown("---")
    
    with tab2:
        st.markdown("### All User Predictions")
        
        all_predictions = db.get_all_predictions()
        
        if not all_predictions:
            st.info("📭 No predictions submitted yet!")
        else:
            # Group by user
            user_preds = {}
            for pred in all_predictions:
                if pred["user_name"] not in user_preds:
                    user_preds[pred["user_name"]] = {}
                user_preds[pred["user_name"]][pred["category_id"]] = {
                    "prediction": pred["prediction"],
                    "submitted_at": pred["submitted_at"]
                }
            
            # Show each user's predictions
            for user, preds in user_preds.items():
                with st.expander(f"👤 {user}'s Predictions", expanded=True):
                    submitted_time = list(preds.values())[0]["submitted_at"]
                    st.caption(f"Last updated: {submitted_time}")
                    
                    for category in config["categories"]:
                        cat_id = category["id"]
                        if cat_id in preds:
                            st.write(f"**{category['name']}:** {preds[cat_id]['prediction']}")
                        else:
                            st.write(f"**{category['name']}:** _No prediction_")
    
    with tab3:
        st.markdown("### Enter the actual Oscar winners")
        
        # Get current winners
        current_winners = db.get_winners()
        
        st.markdown("---")
        winners = {}
        
        for category in config["categories"]:
            st.subheader(f"🏆 {category['name']}")
            
            # Get previous winner if exists
            previous = current_winners.get(category["id"])
            default_index = 0
            if previous and previous in category["nominees"]:
                default_index = category["nominees"].index(previous)
            
            winner = st.selectbox(
                f"Actual winner:",
                options=category["nominees"],
                key=f"winner_{category['id']}",
                index=default_index
            )
            winners[category["id"]] = winner
        
        # Save button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Save Winners", type="primary", use_container_width=True):
                db.save_winners(winners)
                st.success("✅ Winners saved!")
                st.balloons()

def show_results():
    """Show results and scores"""
    st.title("🏆 Results")
    
    winners = db.get_winners()
    scores = db.calculate_scores()
    
    if not winners:
        st.info("⏳ No winners entered yet. Check back after the Oscars!")
        return
    
    if not scores:
        st.info("📭 No predictions submitted yet!")
        return
    
    # Show scores
    st.markdown("### 🎯 Final Scores")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for i, (user, score) in enumerate(sorted_scores, 1):
        total_categories = len(config["categories"])
        percentage = (score / total_categories) * 100
        
        if i == 1:
            st.success(f"🥇 **{user}**: {score}/{total_categories} correct ({percentage:.1f}%) - WINNER! 🎉")
        elif i == 2:
            st.info(f"🥈 **{user}**: {score}/{total_categories} correct ({percentage:.1f}%)")
        else:
            st.write(f"{i}. **{user}**: {score}/{total_categories} correct ({percentage:.1f}%)")
    
    # Show detailed comparison
    st.markdown("---")
    st.markdown("### 📊 Detailed Comparison")
    
    all_predictions = db.get_all_predictions()
    user_preds = {}
    for pred in all_predictions:
        if pred["user_name"] not in user_preds:
            user_preds[pred["user_name"]] = {}
        user_preds[pred["user_name"]][pred["category_id"]] = pred["prediction"]
    
    for category in config["categories"]:
        cat_id = category["id"]
        actual_winner = winners.get(cat_id, "Not set")
        
        st.markdown(f"#### 🎭 {category['name']}")
        st.markdown(f"**Actual Winner:** {actual_winner}")
        
        for user, preds in user_preds.items():
            prediction = preds.get(cat_id, "No prediction")
            is_correct = prediction == actual_winner
            
            if is_correct:
                st.success(f"✅ {user}: {prediction}")
            else:
                st.error(f"❌ {user}: {prediction}")
        
        st.markdown("---")

# Main app
def main():
    # Sidebar navigation
    st.sidebar.title("🎬 Navigation")
    page = st.sidebar.radio("Go to:", ["Make Predictions", "Results", "Admin Panel"])
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"🗓️ Oscars Date: {config['oscars_date']}")
    st.sidebar.info(f"⏰ Deadline: {config['lock_date']}")
    
    if is_locked():
        st.sidebar.warning("🔒 Submissions are LOCKED")
    else:
        st.sidebar.success("🟢 Submissions are OPEN")
    
    # Show selected page
    if page == "Make Predictions":
        show_prediction_form()
    elif page == "Results":
        show_results()
    elif page == "Admin Panel":
        show_admin_panel()

if __name__ == "__main__":
    main()