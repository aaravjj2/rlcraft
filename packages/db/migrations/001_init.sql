CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS pack_build(
  build_id uuid PRIMARY KEY,
  pack_name text NOT NULL,
  pack_version text NOT NULL,
  mc_version text NOT NULL,
  modlist_checksum text NOT NULL,
  config_checksum text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_item(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  item_key text NOT NULL,
  name text NOT NULL,
  mod text NOT NULL,
  raw_json jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS entity_mob(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  mob_key text NOT NULL,
  name text NOT NULL,
  mod text NOT NULL,
  raw_json jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  recipe_key text NOT NULL,
  type text NOT NULL,
  raw_json jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_input(
  id uuid PRIMARY KEY,
  recipe_id uuid NOT NULL REFERENCES recipe(id),
  item_key text NOT NULL,
  qty int NOT NULL,
  meta jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_output(
  id uuid PRIMARY KEY,
  recipe_id uuid NOT NULL REFERENCES recipe(id),
  item_key text NOT NULL,
  qty int NOT NULL,
  meta jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS item_used_in(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  item_key text NOT NULL,
  recipe_id uuid NOT NULL REFERENCES recipe(id)
);

CREATE TABLE IF NOT EXISTS mob_spawn_rule(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  mob_key text NOT NULL,
  dimension text NOT NULL,
  biome text NOT NULL,
  conditions jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS structure(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  structure_key text NOT NULL,
  name text NOT NULL,
  type text NOT NULL,
  raw_json jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS structure_image(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  structure_key text NOT NULL,
  image_url text NOT NULL,
  label_source text NOT NULL,
  meta jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS structure_embedding(
  structure_image_id uuid PRIMARY KEY REFERENCES structure_image(id),
  embedding vector(16) NOT NULL,
  meta jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS page_note(
  id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES pack_build(build_id),
  entity_kind text NOT NULL,
  entity_key text NOT NULL,
  markdown text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_item_build_key ON entity_item(build_id,item_key);
CREATE INDEX IF NOT EXISTS idx_mob_build_key ON entity_mob(build_id,mob_key);
CREATE INDEX IF NOT EXISTS idx_struct_build_key ON structure(build_id,structure_key);
CREATE INDEX IF NOT EXISTS idx_recipe_build_key ON recipe(build_id,recipe_key);
CREATE INDEX IF NOT EXISTS idx_structure_embedding_cos ON structure_embedding USING ivfflat (embedding vector_cosine_ops);
