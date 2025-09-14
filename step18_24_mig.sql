DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='tone_profile') THEN
    ALTER TABLE public.agents ADD COLUMN tone_profile text;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='safety_rating') THEN
    ALTER TABLE public.agents ADD COLUMN safety_rating text;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='safety_score') THEN
    ALTER TABLE public.agents ADD COLUMN safety_score numeric;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='lineage_display') THEN
    ALTER TABLE public.agents ADD COLUMN lineage_display text;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='last_safety_check') THEN
    ALTER TABLE public.agents ADD COLUMN last_safety_check timestamptz;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='usage_cost') THEN
    ALTER TABLE public.agents ADD COLUMN usage_cost numeric;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='published') THEN
    ALTER TABLE public.agents ADD COLUMN published boolean DEFAULT false;
  END IF;
  CREATE INDEX IF NOT EXISTS idx_agents_published ON public.agents(published);

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='parent_id') THEN
    ALTER TABLE public.agents ADD COLUMN parent_id integer NULL;
  END IF;
  CREATE INDEX IF NOT EXISTS idx_agents_parent_id ON public.agents(parent_id);

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='agents' AND column_name='owner_id') THEN
    ALTER TABLE public.agents ADD COLUMN owner_id integer NULL;
  END IF;
END
\$\$;

DO \$\$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid
    WHERE t.relname='agents' AND c.conname='agents_owner_id_fkey'
  ) THEN
    ALTER TABLE public.agents
      ADD CONSTRAINT agents_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE SET NULL;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid
    WHERE t.relname='agents' AND c.conname='agents_parent_id_fkey'
  ) THEN
    ALTER TABLE public.agents
      ADD CONSTRAINT agents_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.agents(id) ON DELETE SET NULL;
  END IF;
END
\$\$;

CREATE TABLE IF NOT EXISTS public.audit_log (
  id serial PRIMARY KEY,
  event_type text NOT NULL,
  actor_user_id integer NULL,
  bot_id integer NULL,
  payload jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON public.audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_bot_id ON public.audit_log(bot_id);
