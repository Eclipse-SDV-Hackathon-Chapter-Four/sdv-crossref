-- Example queries over facts/facts.duckdb. Rebuild first: .venv/bin/python scripts/build_facts.py
-- Run one with the duckdb Python package (see facts/README.md). Statements are separated by semicolons.

-- 1. Version drift on the watch-list: packages/images seen at more than one version across the repos.
SELECT ecosystem, package, versions_seen, repos
FROM pins_vs_current WHERE len(versions_seen) > 1 ORDER BY package, ecosystem;

-- 2. Who pins up-rust 0.7.x (manifest requirement or lockfile resolution).
SELECT repo, manifest_path, ecosystem, version_req, resolved_version
FROM deps WHERE package = 'up-rust' AND coalesce(resolved_version, version_req) LIKE '0.7%'
ORDER BY repo, manifest_path;

-- 3. Draft notes per component (cards count under their cluster).
SELECT coalesce(component, 'cluster:' || cluster) AS component, count(*) AS drafts, list(basename ORDER BY basename) AS notes
FROM notes WHERE status = 'draft' GROUP BY ALL ORDER BY drafts DESC, component;

-- 4. Notes that touch KUKSA (component, tags or applies-to) and are still draft.
SELECT path, type, component, applies_to FROM notes
WHERE status = 'draft'
  AND (component LIKE '%vss-kuksa%' OR list_contains(applies_to, 'vss-kuksa') OR list_contains(tags, 'kuksa'))
ORDER BY path;

-- 5. Dangling links: [[targets]] that resolve to no note or file.
SELECT from_path, to_basename FROM links WHERE NOT resolves ORDER BY from_path, to_basename;

-- 6. Integration gaps: claims between two of the core nine whose maturity is none or idea.
SELECT from_component, to_component, maturity, how, source_path FROM claims
WHERE maturity IN ('none', 'idea')
  AND from_component IN ('iceoryx2', 's-core', 'opensovd', 'vss-kuksa', 'uprotocol', 'ankaios', 'opendut', 'autosd', 'openbsw')
  AND to_component   IN ('iceoryx2', 's-core', 'opensovd', 'vss-kuksa', 'uprotocol', 'ankaios', 'opendut', 'autosd', 'openbsw')
ORDER BY from_component, to_component;

-- 7. Databroker and Zenoh images: which tags are used, by how many files and repos.
SELECT image, coalesce(tag, '(none)') AS tag, count(*) AS files, list(DISTINCT repo ORDER BY repo) AS repos
FROM images WHERE image ILIKE '%databroker%' OR image ILIKE '%zenoh%'
GROUP BY ALL ORDER BY image, tag;

-- 8. Host-port collisions: the same host port published by more than one compose file.
SELECT host_port, count(DISTINCT file_path) AS files, list(DISTINCT repo ORDER BY repo) AS repos
FROM ports WHERE host_port IS NOT NULL
GROUP BY host_port HAVING count(DISTINCT file_path) > 1 ORDER BY files DESC, host_port;

-- 9. SOVD routes per base path (opensovd repos). NEST rows are router prefixes.
SELECT repo, coalesce(base_path_hint, '(none)') AS base_path, method, path, file_path FROM routes
WHERE repo LIKE 'opensovd%' ORDER BY repo, base_path, path, method;

-- 10. VSS paths referenced by more than one repo (the de-facto shared signal set).
SELECT vss_path, count(DISTINCT repo) AS repos, list(DISTINCT repo ORDER BY repo) AS repo_list
FROM vss_paths GROUP BY vss_path HAVING count(DISTINCT repo) > 1 ORDER BY repos DESC, vss_path;

-- 11. Repo freshness: clone HEAD date per repo, oldest first.
SELECT name, head_date, remote_url FROM repos ORDER BY head_date;
