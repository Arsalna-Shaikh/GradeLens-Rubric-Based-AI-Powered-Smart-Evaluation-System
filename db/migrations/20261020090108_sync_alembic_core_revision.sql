INSERT INTO alembic_version (version_num)
SELECT '000000000001'
WHERE NOT EXISTS (SELECT 1 FROM alembic_version WHERE version_num = '000000000001');
