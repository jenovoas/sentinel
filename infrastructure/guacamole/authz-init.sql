INSERT INTO guacamole_entity (name, type)
VALUES
    ('Guacamole Users', 'USER_GROUP'),
    ('Guacamole Admins', 'USER_GROUP')
ON CONFLICT (type, name) DO NOTHING;

INSERT INTO guacamole_user_group (entity_id, disabled)
SELECT entity_id, FALSE
FROM guacamole_entity
WHERE name IN ('Guacamole Users', 'Guacamole Admins')
  AND type = 'USER_GROUP'
ON CONFLICT (entity_id) DO NOTHING;

INSERT INTO guacamole_system_permission (entity_id, permission)
SELECT entity.entity_id, permission.permission::guacamole_system_permission_type
FROM guacamole_entity AS entity
CROSS JOIN (VALUES
    ('CREATE_CONNECTION'),
    ('CREATE_CONNECTION_GROUP'),
    ('CREATE_SHARING_PROFILE'),
    ('AUDIT')
) AS permission(permission)
WHERE entity.name = 'Guacamole Admins'
  AND entity.type = 'USER_GROUP'
ON CONFLICT (entity_id, permission) DO NOTHING;
