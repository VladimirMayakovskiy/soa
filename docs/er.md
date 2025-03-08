erDiagram
    USERS {
        int id PK
        string username
        string email
        string password_hash
        datetime created_at
        datetime updated_at
    }
    SESSIONS {
        int id PK
        int user_id FK
        string token
        datetime start_date
        datetime end_date
        string ip_address
    }
    USER_ROLES {
        int user_id FK
        string role
    }

    USERS ||--o{ SESSIONS : "has"
    USERS ||--|| USER_ROLES : "assigned"

    POSTS {
        int id PK
        int user_id FK
        string title
        string content
        datetime created_at
    }
    COMMENTS {
        int id PK
        int post_id FK
        int user_id FK
        string content
        datetime created_at
        int parent_comment_id FK
    }
    ATTACHMENTS {
        int id PK
        int post_id FK
        string url
        string file_type
        int file_size
        datetime uploaded_at
    }

    USERS ||--o{ POSTS : "creates"
    USERS ||--o{ COMMENTS : "creates"
    POSTS ||--o{ COMMENTS : "has"
    POSTS ||--o{ ATTACHMENTS : "includes"
    COMMENTS ||--o{ COMMENTS : "replies to"

    LIKES {
        int id PK
        int user_id FK
        int post_id FK
        datetime created_at
        string type
    }
    VIEWS {
        int id PK
        int user_id FK
        int post_id FK
        datetime viewed_at
        string view_source 
    }
    ENGAGEMENT_STATS {
        int id PK
        int post_id FK
        int total_likes
        int total_views
        int total_comments
        datetime updated_at
    }

    USERS ||--o{ LIKES : "creates"
    USERS ||--o{ VIEWS : "creates"
    POSTS ||--o{ LIKES : "receives"
    POSTS ||--o{ VIEWS : "receives"
    POSTS ||--o{ ENGAGEMENT_STATS : "aggregates"
    
    