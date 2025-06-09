-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "ltree";

-- Create custom types
CREATE TYPE product_status AS ENUM ('active', 'inactive', 'archived');
CREATE TYPE attribute_type AS ENUM ('string', 'number', 'boolean', 'list', 'date');