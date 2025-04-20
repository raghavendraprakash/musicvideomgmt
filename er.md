# Entity Relationship Diagram

## Entities and Relationships

```
+-------------------+                 +-------------------+
|      users        |                 |   music_videos    |
+-------------------+                 +-------------------+
| id (PK)           |       1         | id (PK)           |
| username          |<--------------->| title             |
| password_hash     |       0..*      | artist            |
| email             |                 | url               |
+-------------------+                 | user_id (FK)      |
                                      | created_at        |
                                      +-------------------+
```

## Schema Details

### users
- **id**: SERIAL PRIMARY KEY
- **username**: VARCHAR(100) UNIQUE NOT NULL
- **password_hash**: VARCHAR(200) NOT NULL
- **email**: VARCHAR(100) UNIQUE NOT NULL

### music_videos
- **id**: SERIAL PRIMARY KEY
- **title**: VARCHAR(200) NOT NULL
- **artist**: VARCHAR(200) NOT NULL
- **url**: VARCHAR(500) NOT NULL
- **user_id**: INTEGER REFERENCES users(id)
- **created_at**: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Relationships Explained

There is a one-to-many relationship between users and music_videos:
- One user can have multiple music videos (0 to many)
- Each music video belongs to exactly one user (or can be null if not associated with any user)

## Constraints

1. The username and email fields in the users table must be unique
2. The user_id in the music_videos table references the id field in the users table
3. Most fields are marked as NOT NULL, indicating they are required

## SQL Schema

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS music_videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    artist VARCHAR(200) NOT NULL,
    url VARCHAR(500) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Entity Details

### users
This entity represents user accounts in the system. Each user has a unique identifier, username, password (stored as a hash for security), and email address. Both username and email must be unique across all users.

### music_videos
This entity represents music videos that can be associated with users. Each music video has a unique identifier, title, artist name, URL to the video, a reference to the user who added it, and a timestamp of when it was created.

## Cardinality
- **users to music_videos**: One-to-many (1:N)
  - A user can have zero or many music videos
  - A music video belongs to exactly one user (or none)

## Design Considerations
- The schema uses SERIAL type for auto-incrementing primary keys
- Foreign key constraints ensure referential integrity
- Timestamp fields automatically record creation time
- Unique constraints prevent duplicate usernames and emails
