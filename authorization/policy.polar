# Base rule for admin users - they can do anything
allow(actor: User, _action, _resource) if actor.is_admin;

# Role-based permissions
role_allow("admin", "manage_roles", "Role");
role_allow("admin", "manage_users", "User");
role_allow("admin", "read", "Document");
role_allow("admin", "write", "Document");
role_allow("admin", "delete", "Document");

role_allow("user", "read", "Document");
role_allow("user", "write", "Document");

# Base authorization rule
allow(actor: User, action, resource_type) if
    role in actor.roles and
    role_allow(role.name, action, resource_type);

# Helper rule to check if user has a role
has_role(user: User, role_name: String) if
    role in user.roles and
    role.name = role_name;

# Allow users to read their own profile
allow(actor, "read", resource) if
    resource matches User and
    actor.id = resource.id;

# Allow users to update their own profile
allow(actor, "write", resource) if
    resource matches User and
    actor.id = resource.id;

# Allow users to read their own profile
allow(actor, "read", resource) if
    resource matches User and
    actor.id = resource.id;

# Allow users to update their own profile
allow(actor, "write", resource) if
    resource matches User and
    actor.id = resource.id;

# Base authorization rules
allow(actor, action, resource_type) if
    has_role(actor, role) and
    role_allow(role, action, resource_type);

# Helper rules
has_role(actor, role) if
    role in actor.roles or
    (role = "user" and not actor.is_admin); 