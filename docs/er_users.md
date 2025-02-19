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
    
    