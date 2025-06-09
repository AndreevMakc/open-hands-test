# 🔐 Stage 5: Authentication & Authorization

## 📋 Обзор этапа

**Цель**: Реализовать полную систему аутентификации и авторизации с JWT токенами, ролевой моделью доступа и управлением пользователями.

**Продолжительность**: 1 неделя

## 🎯 Основные задачи

### 1. 🔑 JWT Authentication
- [ ] JWT token generation и validation
- [ ] Access и Refresh token механизм
- [ ] Token blacklisting для logout
- [ ] Password hashing с bcrypt
- [ ] Login/logout endpoints

### 2. 👥 User Management
- [ ] User entity и repository
- [ ] User registration и profile management
- [ ] Password reset functionality
- [ ] Email verification (опционально)
- [ ] User CRUD operations

### 3. 🛡️ Role-Based Access Control (RBAC)
- [ ] Role и Permission entities
- [ ] Predefined roles (Admin, Manager, User)
- [ ] Permission-based access control
- [ ] Role assignment и management
- [ ] Resource-level permissions

### 4. 🔒 API Security
- [ ] Protected endpoints с JWT middleware
- [ ] Permission decorators
- [ ] Rate limiting
- [ ] CORS security
- [ ] Input validation и sanitization

### 5. 📊 Security Monitoring
- [ ] Login attempt tracking
- [ ] Security event logging
- [ ] Failed authentication monitoring
- [ ] Session management
- [ ] Security metrics

## 🏗️ Архитектурные компоненты

### Domain Layer
```
src/domain/entities/
├── user.py                  # User entity
├── role.py                  # Role entity
└── permission.py            # Permission entity

src/domain/value_objects/
├── email.py                 # Email value object
├── password.py              # Password value object
└── token.py                 # Token value object

src/domain/repositories/
├── user_repository.py       # User repository interface
├── role_repository.py       # Role repository interface
└── auth_repository.py       # Auth repository interface
```

### Infrastructure Layer
```
src/infrastructure/auth/
├── __init__.py
├── jwt_service.py           # JWT token operations
├── password_service.py      # Password hashing/verification
├── auth_middleware.py       # Authentication middleware
└── permission_checker.py    # Permission validation

src/infrastructure/database/models/
├── user_model.py            # User SQLAlchemy model
├── role_model.py            # Role SQLAlchemy model
└── permission_model.py      # Permission SQLAlchemy model

src/infrastructure/repositories/
├── user_repository.py       # User repository implementation
├── role_repository.py       # Role repository implementation
└── auth_repository.py       # Auth repository implementation
```

### Application Layer
```
src/application/dtos/
├── auth_dto.py              # Authentication DTOs
├── user_dto.py              # User management DTOs
└── role_dto.py              # Role management DTOs

src/application/use_cases/
├── auth_use_cases.py        # Authentication use cases
├── user_use_cases.py        # User management use cases
└── role_use_cases.py        # Role management use cases
```

### Presentation Layer
```
src/presentation/api/v1/
├── auth.py                  # Authentication endpoints
├── users.py                 # User management endpoints
└── roles.py                 # Role management endpoints

src/presentation/middleware/
├── auth_middleware.py       # FastAPI auth middleware
└── permission_middleware.py # Permission checking middleware
```

## 🔐 Security Model

### User Roles
```python
ROLES = {
    "SUPER_ADMIN": {
        "description": "Full system access",
        "permissions": ["*"]
    },
    "ADMIN": {
        "description": "Administrative access",
        "permissions": [
            "users.create", "users.read", "users.update", "users.delete",
            "roles.create", "roles.read", "roles.update", "roles.delete",
            "categories.create", "categories.update", "categories.delete",
            "products.create", "products.update", "products.delete",
            "attributes.create", "attributes.update", "attributes.delete",
            "cache.manage"
        ]
    },
    "MANAGER": {
        "description": "Content management access",
        "permissions": [
            "categories.create", "categories.read", "categories.update",
            "products.create", "products.read", "products.update",
            "attributes.create", "attributes.read", "attributes.update",
            "users.read"
        ]
    },
    "USER": {
        "description": "Read-only access",
        "permissions": [
            "categories.read",
            "products.read",
            "attributes.read"
        ]
    },
    "GUEST": {
        "description": "Public access",
        "permissions": [
            "categories.read",
            "products.read"
        ]
    }
}
```

### Permission System
```python
PERMISSIONS = {
    # User management
    "users.create": "Create new users",
    "users.read": "View user information",
    "users.update": "Update user information",
    "users.delete": "Delete users",
    
    # Role management
    "roles.create": "Create new roles",
    "roles.read": "View role information",
    "roles.update": "Update role information",
    "roles.delete": "Delete roles",
    
    # Category management
    "categories.create": "Create categories",
    "categories.read": "View categories",
    "categories.update": "Update categories",
    "categories.delete": "Delete categories",
    
    # Product management
    "products.create": "Create products",
    "products.read": "View products",
    "products.update": "Update products",
    "products.delete": "Delete products",
    
    # Attribute management
    "attributes.create": "Create attributes",
    "attributes.read": "View attributes",
    "attributes.update": "Update attributes",
    "attributes.delete": "Delete attributes",
    
    # Cache management
    "cache.manage": "Manage cache system",
    
    # System administration
    "system.admin": "System administration"
}
```

## 🔧 JWT Configuration

### Token Structure
```python
JWT_CONFIG = {
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
    "issuer": "product-catalog-service",
    "audience": "product-catalog-users"
}

ACCESS_TOKEN_PAYLOAD = {
    "sub": "user_id",
    "email": "user_email",
    "roles": ["role1", "role2"],
    "permissions": ["perm1", "perm2"],
    "iat": "issued_at",
    "exp": "expires_at",
    "iss": "issuer",
    "aud": "audience",
    "type": "access"
}

REFRESH_TOKEN_PAYLOAD = {
    "sub": "user_id",
    "iat": "issued_at",
    "exp": "expires_at",
    "iss": "issuer",
    "aud": "audience",
    "type": "refresh"
}
```

## 📊 Database Schema

### User Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Role Table
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Permission Table
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User-Role Association
```sql
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);
```

### Role-Permission Association
```sql
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
```

## 🔒 API Security Implementation

### Protected Endpoints
```python
# Authentication required
@router.get("/protected")
@require_auth
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Access granted"}

# Permission required
@router.post("/admin-only")
@require_permission("system.admin")
async def admin_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Admin access granted"}

# Role required
@router.get("/manager-only")
@require_role("MANAGER")
async def manager_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": "Manager access granted"}
```

### Middleware Integration
```python
# Authentication middleware
app.add_middleware(AuthenticationMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# CORS middleware with security headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 📋 API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset confirmation
- `GET /api/v1/auth/me` - Get current user info

### User Management Endpoints
- `GET /api/v1/users/` - List users (Admin only)
- `POST /api/v1/users/` - Create user (Admin only)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user (Admin only)
- `PUT /api/v1/users/{id}/roles` - Assign roles (Admin only)
- `GET /api/v1/users/{id}/permissions` - Get user permissions

### Role Management Endpoints
- `GET /api/v1/roles/` - List roles
- `POST /api/v1/roles/` - Create role (Admin only)
- `GET /api/v1/roles/{id}` - Get role details
- `PUT /api/v1/roles/{id}` - Update role (Admin only)
- `DELETE /api/v1/roles/{id}` - Delete role (Admin only)
- `PUT /api/v1/roles/{id}/permissions` - Assign permissions (Admin only)

## 🧪 Testing Strategy

### Authentication Tests
- [ ] JWT token generation and validation
- [ ] Login/logout functionality
- [ ] Password hashing and verification
- [ ] Token expiration handling
- [ ] Refresh token mechanism

### Authorization Tests
- [ ] Role-based access control
- [ ] Permission checking
- [ ] Protected endpoint access
- [ ] Unauthorized access prevention
- [ ] Cross-user data access prevention

### Security Tests
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Input validation

## 📊 Security Monitoring

### Metrics to Track
```python
SECURITY_METRICS = {
    "login_attempts": "Total login attempts",
    "failed_logins": "Failed login attempts",
    "successful_logins": "Successful logins",
    "token_refreshes": "Token refresh requests",
    "unauthorized_access": "Unauthorized access attempts",
    "rate_limit_hits": "Rate limit violations",
    "password_resets": "Password reset requests"
}
```

### Security Events
```python
SECURITY_EVENTS = {
    "USER_LOGIN": "User successful login",
    "USER_LOGOUT": "User logout",
    "LOGIN_FAILED": "Failed login attempt",
    "TOKEN_EXPIRED": "Token expiration",
    "UNAUTHORIZED_ACCESS": "Unauthorized access attempt",
    "PERMISSION_DENIED": "Permission denied",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
    "PASSWORD_CHANGED": "Password changed",
    "ROLE_ASSIGNED": "Role assigned to user",
    "PERMISSION_GRANTED": "Permission granted"
}
```

## 🔄 Implementation Steps

### Week 1: Authentication & Authorization
**Day 1-2**: Core authentication
- JWT service implementation
- Password hashing service
- User entity and repository
- Basic login/logout endpoints

**Day 3-4**: Authorization system
- Role and permission entities
- RBAC implementation
- Permission checking middleware
- Protected endpoints

**Day 5-7**: User management
- User CRUD operations
- Role assignment
- Security monitoring
- API documentation

## 🚀 Expected Outcomes

После завершения Stage 5:
- ✅ **Secure Authentication**: JWT-based authentication system
- ✅ **Role-Based Access**: Flexible RBAC system
- ✅ **User Management**: Complete user lifecycle management
- ✅ **API Security**: Protected endpoints with proper authorization
- ✅ **Security Monitoring**: Comprehensive security event tracking
- ✅ **Production Ready**: Enterprise-grade security implementation

## 🔄 Next Stage Preview

**Stage 6**: Testing, CI/CD & Production Deployment
- Comprehensive testing suite
- CI/CD pipeline setup
- Performance testing
- Production deployment guide
- Monitoring and alerting