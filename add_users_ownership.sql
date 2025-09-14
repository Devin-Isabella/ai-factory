-- Users (very small dev table)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name  TEXT,
  role  TEXT DEFAULT 'owner',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agents ownership (nullable; set on create when logged in)
ALTER TABLE IF EXISTS agents
  ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id);

-- Helpful index
CREATE INDEX IF NOT EXISTS idx_agents_owner ON agents(owner_id);

-- (Optional) add updated_at if your store code orders by it
ALTER TABLE IF EXISTS agents
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
