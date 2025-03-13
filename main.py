import streamlit as st
import logging
from database import get_database_connection, init_db
from auth import hash_password, verify_password, create_access_token, verify_token
from logger_config import setup_logger, log_streamlit_event
import traceback
import time

# Setup logger
logger = setup_logger()
# initialize db
init_db()

# Add performance monitoring
def log_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            raise
    return wrapper

@log_performance
def signup():
    st.subheader("Create New Account")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_email = st.text_input("Email")
    
    if st.button("Signup"):
        cur = None
        conn = None
        try:
            logger.info(f"Attempting signup for user: {new_username}")
            conn = get_database_connection()
            cur = conn.cursor()
            
            # Check if username exists
            cur.execute("SELECT id FROM users WHERE username = %s", (new_username,))
            if cur.fetchone() is not None:
                logger.warning(f"Signup failed: Username {new_username} already exists")
                st.error("Username already exists!")
                return
            
            # Create new user
            password_hash = hash_password(new_password)
            cur.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                (new_username, password_hash, new_email)
            )
            conn.commit()
            logger.info(f"User created successfully: {new_username}")
            st.success("Account created successfully!")
            
            # Log event
            log_streamlit_event(logger, "SIGNUP", f"New user created: {new_username}")
            
        except Exception as e:
            logger.error(f"Signup error for user {new_username}: {str(e)}\n{traceback.format_exc()}")
            st.error("An error occurred during signup")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()  # Close the connection if it was opened

@log_performance
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        cur = None
        conn = None
        try:
            logger.info(f"Login attempt for user: {username}")
            conn = get_database_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            
            if result and verify_password(password, result[1]):
                token = create_access_token({"user_id": result[0], "username": username})
                st.session_state['token'] = token
                st.session_state['username'] = username
                logger.info(f"Successful login for user: {username}")
                st.success("Logged in successfully!")
                
                # Log event
                log_streamlit_event(logger, "LOGIN", f"User logged in: {username}")
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                st.error("Invalid username or password")
                
        except Exception as e:
            logger.error(f"Login error for user {username}: {str(e)}\n{traceback.format_exc()}")
            st.error("An error occurred during login")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()  # Close the connection if it was opened

@log_performance
def manage_music_videos():
    st.subheader("Music Video Management")
    
    # Add new music video
    st.write("Add New Music Video")
    title = st.text_input("Title")
    artist = st.text_input("Artist")
    url = st.text_input("Video URL")
    
    if st.button("Add Video"):
        cur = None
        conn = None
        try:
            logger.info(f"Attempting to add video: {title}")
            conn = get_database_connection()
            cur = conn.cursor()
            
            user_id = verify_token(st.session_state['token'])['user_id']
            cur.execute(
                "INSERT INTO music_videos (title, artist, url, user_id) VALUES (%s, %s, %s, %s)",
                (title, artist, url, user_id)
            )
            conn.commit()
            logger.info(f"Video added successfully: {title}")
            st.success("Video added successfully!")
            
            # Log event
            log_streamlit_event(logger, "ADD_VIDEO", f"New video added: {title}", 
                              {"artist": artist, "user_id": user_id})
            
        except Exception as e:
            logger.error(f"Error adding video {title}: {str(e)}\n{traceback.format_exc()}")
            st.error("An error occurred while adding the video")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()  # Close the connection if it was opened

@log_performance
def manage_music_videos():
    st.subheader("Music Video Management")
    
    # Create tabs for different operations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add", "List", "Search", "Modify", "Delete"])
    
    # Tab 1: Add new music video
    with tab1:
        st.write("Add New Music Video")
        title = st.text_input("Title", key="add_title")
        artist = st.text_input("Artist", key="add_artist")
        url = st.text_input("Video URL", key="add_url")
        
        if st.button("Add Video"):
            cur = None
            conn = None
            try:
                logger.info(f"Attempting to add video: {title}")
                conn = get_database_connection()
                cur = conn.cursor()
                
                user_id = verify_token(st.session_state['token'])['user_id']
                cur.execute(
                    "INSERT INTO music_videos (title, artist, url, user_id) VALUES (%s, %s, %s, %s)",
                    (title, artist, url, user_id)
                )
                conn.commit()
                logger.info(f"Video added successfully: {title}")
                st.success("Video added successfully!")
                
                # Log event
                log_streamlit_event(logger, "ADD_VIDEO", f"New video added: {title}", 
                                  {"artist": artist, "user_id": user_id})
                
            except Exception as e:
                logger.error(f"Error adding video {title}: {str(e)}\n{traceback.format_exc()}")
                st.error("An error occurred while adding the video")
            finally:
                if cur: cur.close()
                if conn: conn.close()

    # Tab 2: List all videos
    with tab2:
        st.write("Your Music Videos")
        try:
            conn = get_database_connection()
            cur = conn.cursor()
            user_id = verify_token(st.session_state['token'])['user_id']
            
            cur.execute("""
                SELECT id, title, artist, url, created_at 
                FROM music_videos 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (user_id,))
            
            videos = cur.fetchall()
            
            if videos:
                for video in videos:
                    with st.expander(f"{video[1]} - {video[2]}"):
                        st.write(f"URL: {video[3]}")
                        st.write(f"Added on: {video[4]}")
            else:
                st.info("No videos found")
                
        except Exception as e:
            logger.error(f"Error listing videos: {str(e)}")
            st.error("Error retrieving videos")
        finally:
            if cur: cur.close()
            if conn: conn.close()

    # Tab 3: Search videos
    with tab3:
        st.write("Search Videos")
        search_term = st.text_input("Enter search term")
        search_by = st.selectbox("Search by", ["Title", "Artist"])
        
        if st.button("Search"):
            try:
                conn = get_database_connection()
                cur = conn.cursor()
                user_id = verify_token(st.session_state['token'])['user_id']
                
                if search_by == "Title":
                    cur.execute("""
                        SELECT id, title, artist, url 
                        FROM music_videos 
                        WHERE user_id = %s AND title ILIKE %s
                    """, (user_id, f"%{search_term}%"))
                else:
                    cur.execute("""
                        SELECT id, title, artist, url 
                        FROM music_videos 
                        WHERE user_id = %s AND artist ILIKE %s
                    """, (user_id, f"%{search_term}%"))
                
                results = cur.fetchall()
                if results:
                    for result in results:
                        with st.expander(f"{result[1]} - {result[2]}"):
                            st.write(f"URL: {result[3]}")
                else:
                    st.info("No matching videos found")
                    
            except Exception as e:
                logger.error(f"Error searching videos: {str(e)}")
                st.error("Error searching videos")
            finally:
                if cur: cur.close()
                if conn: conn.close()

    # Tab 4: Modify video
    with tab4:
        st.write("Modify Video")
        try:
            conn = get_database_connection()
            cur = conn.cursor()
            user_id = verify_token(st.session_state['token'])['user_id']
            
            # Get list of user's videos
            cur.execute("SELECT id, title FROM music_videos WHERE user_id = %s", (user_id,))
            videos = cur.fetchall()
            
            if videos:
                video_to_modify = st.selectbox(
                    "Select video to modify",
                    options=videos,
                    format_func=lambda x: x[1]
                )
                
                # Get current video details
                cur.execute("""
                    SELECT title, artist, url 
                    FROM music_videos 
                    WHERE id = %s AND user_id = %s
                """, (video_to_modify[0], user_id))
                
                current_video = cur.fetchone()
                
                if current_video:
                    new_title = st.text_input("New Title", value=current_video[0])
                    new_artist = st.text_input("New Artist", value=current_video[1])
                    new_url = st.text_input("New URL", value=current_video[2])
                    
                    if st.button("Update Video"):
                        try:
                            cur.execute("""
                                UPDATE music_videos 
                                SET title = %s, artist = %s, url = %s 
                                WHERE id = %s AND user_id = %s
                            """, (new_title, new_artist, new_url, video_to_modify[0], user_id))
                            conn.commit()
                            st.success("Video updated successfully!")
                            log_streamlit_event(logger, "UPDATE_VIDEO", f"Video updated: {new_title}")
                        except Exception as e:
                            logger.error(f"Error updating video: {str(e)}")
                            st.error("Error updating video")
            else:
                st.info("No videos available to modify")
                
        except Exception as e:
            logger.error(f"Error in modify section: {str(e)}")
            st.error("Error loading videos")
        finally:
            if cur: cur.close()
            if conn: conn.close()

    # Tab 5: Delete video
    with tab5:
        st.write("Delete Video")
        try:
            conn = get_database_connection()
            cur = conn.cursor()
            user_id = verify_token(st.session_state['token'])['user_id']
            
            # Get list of user's videos
            cur.execute("SELECT id, title FROM music_videos WHERE user_id = %s", (user_id,))
            videos = cur.fetchall()
            
            if videos:
                video_to_delete = st.selectbox(
                    "Select video to delete",
                    options=videos,
                    format_func=lambda x: x[1],
                    key="delete_select"
                )
                
                if st.button("Delete Video"):
                    if st.checkbox("Are you sure you want to delete this video?"):
                        try:
                            cur.execute("""
                                DELETE FROM music_videos 
                                WHERE id = %s AND user_id = %s
                            """, (video_to_delete[0], user_id))
                            conn.commit()
                            st.success("Video deleted successfully!")
                            log_streamlit_event(logger, "DELETE_VIDEO", f"Video deleted: {video_to_delete[1]}")
                        except Exception as e:
                            logger.error(f"Error deleting video: {str(e)}")
                            st.error("Error deleting video")
            else:
                st.info("No videos available to delete")
                
        except Exception as e:
            logger.error(f"Error in delete section: {str(e)}")
            st.error("Error loading videos")
        finally:
            if cur: cur.close()
            if conn: conn.close()

def main():
    try:
        logger.info("Application started")
        
        # Initialize session states if not exists
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        if 'show_profile' not in st.session_state:
            st.session_state.show_profile = False

        # Sidebar Configuration
        with st.sidebar:
            st.image("images/logo.png", width=200)  # Add your logo
            st.title("Music Video Manager")
            
            if 'token' in st.session_state:
                # Logged-in user menu
                st.write(f"👤 Welcome, {st.session_state['username']}!")
                
                # Main Navigation
                st.subheader("Navigation")
                nav_options = {
                    "🎵 My Videos": "videos",
                    "📊 Dashboard": "dashboard",
                    "⚙️ Settings": "settings"
                }
                
                for label, page in nav_options.items():
                    if st.button(label, key=f"nav_{page}"):
                        st.session_state.page = page
                        st.session_state.show_profile = False
                
                # User Actions
                st.subheader("User Actions")

                if st.button("🚪 Logout"):
                    logger.info(f"User logged out: {st.session_state['username']}")
                    st.session_state.clear()
                    st.experimental_rerun()
            
            else:
                # Non-logged-in user menu
                menu = ["🔑 Login", "📝 Signup", "🔄 Reset Password"]
                choice = st.selectbox("Menu", menu)
                
                if choice == "🔑 Login":
                    st.session_state.page = "login"
                elif choice == "📝 Signup":
                    st.session_state.page = "signup"
                else:
                    st.session_state.page = "reset_password"
            
            # Footer
            st.sidebar.markdown("---")
            st.sidebar.caption("© 2024 Music Video Manager")
            st.sidebar.caption("[Terms of Service](/) | [Privacy Policy](/)")

        # Main Content Area
        if 'token' not in st.session_state:
            # Non-logged-in user content
            if st.session_state.page == "login":
                login()
            elif st.session_state.page == "signup":
                signup()
            elif st.session_state.page == "reset_password":
                reset_password()
            
        else:
            # Logged-in user content
            if st.session_state.show_profile:
                display_user_profile()
            else:
                if st.session_state.page == "home":
                    display_home()
                elif st.session_state.page == "videos":
                    manage_music_videos()
                elif st.session_state.page == "search":
                    display_search()
                elif st.session_state.page == "dashboard":
                    display_dashboard()
                elif st.session_state.page == "settings":
                    display_settings()

    except Exception as e:
        logger.critical(f"Critical application error: {str(e)}\n{traceback.format_exc()}")
        st.error("An unexpected error occurred. Please try again later.")

# New helper functions for different pages
def display_home():
    st.title("🏠 Welcome to Music Video Manager")
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Videos", get_user_video_count())
    with col2:
        st.metric("Recent Additions", get_recent_additions_count())
    with col3:
        st.metric("Categories", get_user_categories_count())
    
    # Recent Activity
    st.subheader("Recent Activity")
    display_recent_activity()
    
    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add New Video"):
            st.session_state.page = "videos"
    with col2:
        if st.button("🔍 Search Videos"):
            st.session_state.page = "search"
    with col3:
        if st.button("📊 View Stats"):
            st.session_state.page = "dashboard"

def display_search():
    st.title("🔍 Search Videos")
    # Advanced search implementation
    search_term = st.text_input("Search term")
    col1, col2 = st.columns(2)
    with col1:
        search_by = st.multiselect(
            "Search in",
            ["Title", "Artist", "Category", "Tags"]
        )
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Recent", "Title", "Artist", "Most Viewed"]
        )
    
    # Add your search implementation here

def display_dashboard():
    st.title("📊 Dashboard")
    
    # Statistics
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Video Statistics")
        # Add charts/graphs here
    with col2:
        st.subheader("Activity Timeline")
        # Add timeline visualization here
    
    # Additional metrics and visualizations

def display_settings():
    st.title("⚙️ Settings")
    
    # User Preferences
    st.subheader("User Preferences")
    theme = st.selectbox("Theme", ["Light", "Dark", "System"])
    language = st.selectbox("Language", ["English", "Spanish", "French"])
    
    # Notification Settings
    st.subheader("Notifications")
    email_notifications = st.checkbox("Email Notifications")
    
    # Security Settings
    st.subheader("Security")
    if st.button("Change Password"):
        # Add change password logic
        pass
    
    # Save Settings
    if st.button("Save Settings"):
        save_user_settings(theme, language, email_notifications)
        st.success("Settings saved successfully!")

def display_user_profile():
    st.title("👤 User Profile")
    
    # User Info
    user_info = get_user_info()
    col1, col2 = st.columns(2)
    with col1:
        st.image("default_avatar.png", width=200)
        st.button("Change Avatar")
    with col2:
        st.text_input("Username", value=user_info['username'], disabled=True)
        email = st.text_input("Email", value=user_info['email'])
        name = st.text_input("Full Name", value=user_info.get('name', ''))
    
    # Profile Actions
    if st.button("Update Profile"):
        update_user_profile(email, name)
        st.success("Profile updated successfully!")

# Helper functions for data retrieval
def get_user_video_count():
    # Implement database query to get user's video count
    return 0

def get_recent_additions_count():
    # Implement database query to get recent additions count
    return 0

def get_user_categories_count():
    # Implement database query to get categories count
    return 0

def display_recent_activity():
    # Implement recent activity display
    pass

def get_user_info():
    # Implement user info retrieval
    return {"username": "", "email": "", "name": ""}

def save_user_settings(theme, language, email_notifications):
    # Implement settings save logic
    pass

def update_user_profile(email, name):
    # Implement profile update logic
    pass

if __name__ == "__main__":
    main()
