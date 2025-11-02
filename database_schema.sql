CREATE TABLE users (
    "id" SERIAL PRIMARY KEY,
    "telegram_id" text UNIQUE NOT NULL
);

CREATE TABLE expenses (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES users("id"),
    "description" text NOT NULL,
    "amount" money NOT NULL,
    "category" text NOT NULL,
    "added_at" timestamp NOT NULL
);

CREATE INDEX idx_expenses_user_id ON expenses("user_id");
CREATE INDEX idx_expenses_added_at ON expenses("added_at");
CREATE INDEX idx_expenses_category ON expenses("category");
