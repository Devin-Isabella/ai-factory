ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS tone_profile text;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS safety_rating text;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS safety_score numeric;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS lineage_display text;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS last_safety_check timestamptz;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS usage_cost numeric;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS published boolean DEFAULT false;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS parent_id integer NULL;
ALTER TABLE public.agents ADD COLUMN IF NOT EXISTS owner_id integer NULL;
CREATE INDEX IF NOT EXISTS idx_agents_published ON public.agents(published);
CREATE INDEX IF NOT EXISTS idx_agents_parent_id ON public.agents(parent_id);
DO }
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid
    WHERE t.relname='agents' AND c.conname='agents_owner_id_fkey'
  ) THEN
    ALTER TABLE public.agents
      ADD CONSTRAINT agents_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE SET NULL;
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid
    WHERE t.relname='agents' AND c.conname='agents_parent_id_fkey'
  ) THEN
    ALTER TABLE public.agents
      ADD CONSTRAINT agents_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.agents(id) ON DELETE SET NULL;
  END IF;
END
};
