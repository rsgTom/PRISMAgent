# Supabase Integration (Python Backend)

This directory contains utilities for integrating Supabase with the PRISMAgent Python backend.

## Important Note

The Next.js/TypeScript Supabase integration has been moved to the `frontend/src/utils/supabase` directory. This directory is reserved for Python-specific Supabase functionality used by the backend.

## Setup

Ensure the following environment variables are set in your `.env` file:

```text
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key  # This is the service role key, not the anon key
```

## Future Implementation

The Python Supabase client will be implemented in this directory to provide database integration for the backend services. This will include:

- User management
- Data storage for agents
- Vector storage for embeddings
- File storage

## Security Considerations

- Never expose the service role key in client-side code
- Use proper authentication in API endpoints
- Implement proper row-level security (RLS) policies in Supabase
