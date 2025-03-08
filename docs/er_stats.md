erDiagram
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

    LIKES ||--o{ ENGAGEMENT_STATS : "aggregated in"
    VIEWS ||--o{ ENGAGEMENT_STATS : "aggregated in" 
        
    