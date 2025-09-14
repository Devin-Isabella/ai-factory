-- Agents (bots) — extend existing
ALTER TABLE IF EXISTS agents
  ADD COLUMN IF NOT EXISTS published BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS parent_id INTEGER,
  ADD COLUMN IF NOT EXISTS last_safety_check_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS last_safe_version_id INTEGER,
  ADD COLUMN IF NOT EXISTS sandbox BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS usage_cost NUMERIC DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS tone_profile VARCHAR(64),
  ADD COLUMN IF NOT EXISTS safety_rating VARCHAR(32),
  ADD COLUMN IF NOT EXISTS lineage_brain_only VARCHAR(64);

-- Bot versions (snapshots)
CREATE TABLE IF NOT EXISTS bot_versions (
  id SERIAL PRIMARY KEY,
  bot_id INTEGER NOT NULL,
  spec JSON NOT NULL,
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Safety checks
CREATE TABLE IF NOT EXISTS safety_checks (
  id SERIAL PRIMARY KEY,
  bot_id INTEGER NOT NULL,
  version_id INTEGER,
  passed BOOLEAN NOT NULL,
  scores JSON,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage blocks (prepaid)
CREATE TABLE IF NOT EXISTS usage_blocks (
  id SERIAL PRIMARY KEY,
  bot_id INTEGER NOT NULL,
  interactions INTEGER NOT NULL,
  amount_usd NUMERIC NOT NULL,
  stripe_payment_id TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Funds ledgers
CREATE TABLE IF NOT EXISTS funds_local (
  id SERIAL PRIMARY KEY,
  bot_id INTEGER NOT NULL,
  amount_usd NUMERIC NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS funds_global (
  id SERIAL PRIMARY KEY,
  amount_usd NUMERIC NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Adoptions & lineage
CREATE TABLE IF NOT EXISTS adoptions (
  id SERIAL PRIMARY KEY,
  parent_bot_id INTEGER NOT NULL,
  child_bot_id INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Append-only audit log
CREATE TABLE IF NOT EXISTS audit_logs (
  id SERIAL PRIMARY KEY,
  actor TEXT,
  action TEXT NOT NULL,
  meta JSON,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
