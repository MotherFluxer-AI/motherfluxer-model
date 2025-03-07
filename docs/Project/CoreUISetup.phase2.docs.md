# Detailed Implementation Plan for Core UI Components Development

## 1. AWS Infrastructure Setup

### 1.1 VPC Configuration
```bash
# VPC Requirements:
- Use existing VPC: vpc-090654194e77018e7
- CIDR: 10.0.0.0/16
- DNS Support: Enabled
- DNS Hostnames: Enabled

# Subnet Selection:
- Use public subnets for UI EC2:
  - us-east-2a: subnet-0399f7d7ee1b84ad8 (10.0.0.0/20)
  - us-east-2b: subnet-01b4834f23685991a (10.0.16.0/20)
```

### 1.2 Security Group Configuration
```bash
# Create new Security Group: motherfluxer-ui-sg
Inbound Rules:
- tcp:22 from your-ip/32 (SSH)
- tcp:80 from 0.0.0.0/0 (HTTP)
- tcp:443 from 0.0.0.0/0 (HTTPS)
- tcp:3000 from 0.0.0.0/0 (Next.js)

Outbound Rules:
- tcp:443 to 0.0.0.0/0 (HTTPS)
- tcp:3000 to sg-00ce1a90e17c09aa2 (API access)
```

### 1.3 EC2 Configuration
```bash
# EC2 Requirements:
- Instance Type: t2.micro (can scale up if needed)
- OS: Ubuntu Server 22.04 LTS
- Storage: 20GB gp3 SSD
- IAM Role: MotherFluxerEC2Role
  - Verify access to:
    - ssm:GetParameter
    - secretsmanager:GetSecretValue
    - ec2:DescribeInstances
```

## 2. Project Setup Requirements

### 2.1 Next.js Project Initialization
```bash
# Create project directory
sudo mkdir -p /var/www/motherfluxer-ui
sudo chown -R ubuntu:ubuntu /var/www/motherfluxer-ui
cd /var/www/motherfluxer-ui

# Initialize Next.js project
npx create-next-app@latest . --typescript --tailwind --eslint
```

### 2.2 Project Structure
```bash
/src
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   └── MessageDisplay.tsx
│   ├── model/
│   │   ├── ModelSelector.tsx
│   │   └── InstanceStatus.tsx
│   ├── routing/
│   │   ├── LoadBalancer.tsx
│   │   ├── HealthChecker.tsx
│   │   └── FailoverHandler.tsx
│   └── common/
│       ├── ErrorBoundary.tsx
│       └── LoadingIndicator.tsx
├── lib/
│   ├── api/
│   ├── auth/
│   └── utils/
└── tests/
    ├── components/
    ├── integration/
    └── unit/
```

### 2.3 Additional Dependencies
```json
{
  "dependencies": {
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/react": "^14.2.0",
    "@testing-library/user-event": "^14.5.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "prettier": "^3.2.0",
    "socket.io-client": "^4.7.0",
    "zustand": "^4.5.0"
  }
}
```

## 3. Core Configuration

### 3.1 TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### 3.2 ESLint Configuration
```json
{
  "extends": [
    "next/core-web-vitals",
    "prettier"
  ],
  "rules": {
    "no-unused-vars": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### 3.3 Nginx Configuration
```nginx
server {
    listen 80;
    server_name motherfluxer-ui.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3.4 SSL Setup
```bash
# SSL Certificate Requirements
- Domain validation
- Wildcard certificate for subdomains
- Auto-renewal configuration
- Security headers implementation
```

### 3.5 Environment Variables
```bash
# Required Environment Variables
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.motherfluxer.com
NEXT_PUBLIC_WS_URL=wss://api.motherfluxer.com
REDIS_URL=motherfluxer-redis-tqayhw.serverless.use2.cache.amazonaws.com
DB_HOST=motherfluxerdb.c322i2ssm4z8.us-east-2.rds.amazonaws.com
```

## 4. Database Integration

### 4.1 Connection Settings
```bash
# Database Configuration
- Host: motherfluxerdb.c322i2ssm4z8.us-east-2.rds.amazonaws.com
- Port: 5432
- SSL: Required
- Max Connections: 5
- Min Connections: 0
- Idle Timeout: 10000ms
```

### 4.2 Required Tables
```sql
# Table: users
- id (uuid) PRIMARY KEY
- email (varchar) UNIQUE
- hashed_password (varchar)
- role (varchar) NOT NULL DEFAULT 'user'
- is_active (boolean) DEFAULT true
- request_limit (integer) DEFAULT 100
- created_at (timestamp with time zone) DEFAULT CURRENT_TIMESTAMP
- last_login (timestamp with time zone)

Constraints:
- email_format: email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
- email_length: length(email) >= 3 AND length(email) <= 255
- password_length: length(hashed_password) = 60

# Table: model_instances
- id (uuid) PRIMARY KEY
- admin_id (uuid) REFERENCES users(id)
- instance_name (varchar) UNIQUE
- host_address (varchar)
- health_score (integer) DEFAULT 100
- is_active (boolean) DEFAULT true
- version (varchar)
- registered_at (timestamp with time zone) DEFAULT CURRENT_TIMESTAMP
- last_health_check (timestamp with time zone)
- container_version (varchar)

# Table: rate_limits
- id (uuid) PRIMARY KEY
- user_id (uuid) REFERENCES users(id)
- window_start (timestamp with time zone) NOT NULL
- request_count (integer) DEFAULT 0
- last_request (timestamp with time zone)

Indexes:
- users_email_key: UNIQUE btree (email)
- idx_model_instances_admin: btree (admin_id)
- idx_model_instances_health: btree (health_score, last_health_check)
- idx_rate_limits_last_request: btree (last_request)
- idx_rate_limits_user_window: btree (user_id, window_start)
- rate_limits_user_window_key: UNIQUE (user_id, window_start)

Constraints:
- request_count_min: request_count >= 0
```

## 5. Redis Integration

### 5.1 Connection Settings
```bash
# Redis Cluster Settings
- Host: motherfluxer-redis-tqayhw.serverless.use2.cache.amazonaws.com
- Port: 6379
- Mode: cluster
- Version: 7.1
- TLS: Required
- Performance baseline: ~7.50ms latency
```

### 5.2 Cache Strategy
```bash
# Cache Usage
- Session management
- Rate limiting state
- Instance health states
- Routing decisions
- Performance metrics
```

## 6. Model Instance Management

### 6.1 Health Monitoring
```bash
# Health Check System
- Regular status polling
- Performance metric collection
- Automatic failover triggers
- Health score calculation (baseline 100)
- Health metrics tracked in database with timestamps
- Performance baseline monitoring:
  - Redis latency: ~7.50ms baseline
  - Database connection pooling metrics
  - Instance response times
```

### 6.2 Instance Registration
```bash
# Registration Requirements
- Admin privileges required
- Unique instance name
- Valid host address
- Health check confirmation
- Version information

# Instance States
- Active/Inactive tracking
- Health score monitoring
- Performance metrics collection
```

### 6.3 Load Balancing
```bash
# Load Balancing Strategy
- Round-robin base implementation
- Health score consideration
- Geographic optimization
- Performance-based routing
```

## 7. Testing Requirements

### 7.1 Testing Setup
```bash
# Test Environment Setup
- Jest configuration
- React Testing Library setup
- Mock service worker
- Test database configuration
```

### 7.2 Required Test Coverage
```bash
# Component Tests
- UI component rendering
- User interactions
- State management
- Error handling

# Integration Tests
- Authentication flow
- Routing system
- Health monitoring
- Load balancing

# Performance Tests
- Database connection pooling
- Redis cluster response
- Rate limiting accuracy
- Load balancing efficiency
```

## 8. Security Implementation

### 8.1 Authentication System
```bash
# Security Features
- JWT implementation
  - User token expiry: 24h
  - Instance token expiry: 30d
- Rate limiting
  - Default limit: 100 requests per window
  - Window tracking in rate_limits table
  - Redis-based rate limit state caching
- CSRF protection
- XSS prevention
- Password requirements:
  - BCrypt hashing (60 characters)
- Email validation:
  - Format validation via regex
  - Length: 3-255 characters
```

### 8.2 Access Control
```bash
# User Management
- Role-based access control
- Permission validation
- Session management
- Activity logging
```

## 9. Deployment Process

### 9.1 Build Process
```bash
# Build Steps
- Environment validation
- Dependency installation
- TypeScript compilation
- Asset optimization
```

### 9.2 Deployment Requirements
```bash
# Deployment Checklist
- SSL certificate installation
- Environment variable verification
- Database migration execution
- Service restart procedures
```

## 10. Next Implementation Steps

1. Component Implementation
   - Choose a component to implement first
   - Set up its type definitions
   - Create the component
   - Write tests

2. Available Components for Implementation:
   - Chat Interface Components
   - Model Selection Components
   - Status Components
   - Common UI Components
   - Routing Visualization Components

3. Testing Focus Areas:
   - Component rendering
   - User interactions
   - State management
   - Error handling
   - Integration tests

4. Production Considerations:
   - Environment variables
   - API endpoint configuration
   - Error logging
   - Performance monitoring
   - Backup strategy

Note: Implementation will follow requirements from Initial Project Plan and ensure compatibility with future expansion plans. The UI will communicate with the private AI infrastructure through secure API endpoints. 