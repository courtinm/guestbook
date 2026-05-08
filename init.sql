CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO messages (author, content)
SELECT 'alice', 'Hello from Alice!'
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE author = 'alice');

INSERT INTO messages (author, content)
SELECT 'bob', 'Hey everyone, great app!'
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE author = 'bob');
