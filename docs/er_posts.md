erDiagram
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
        int parent_comment_id
    }
    ATTACHMENTS {
        int id PK
        int post_id FK
        string url
        string file_type
        int file_size
        datetime uploaded_at
    }

    POSTS ||--o{ COMMENTS: "has"
    POSTS ||--o{ ATTACHMENTS : "includes"
    COMMENTS ||--o{ COMMENTS : "replies to"