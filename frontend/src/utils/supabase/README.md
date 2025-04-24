# Supabase Integration

This directory contains utilities for integrating Supabase with the PRISMAgent frontend.

## Files

- `server.ts`: Server-side Supabase client for use in Next.js Server Components and API Routes
- `client.ts`: Client-side Supabase client for use in browser/client components
- `SupabaseProvider.tsx`: React context provider for easy access to Supabase client in client components

## Setup

1. Create a `.env.local` file in the frontend directory with your Supabase credentials:

    ```text
    NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
    NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
    ```

2. Wrap your application with the `SupabaseProvider` in your root layout:

    ```tsx
    // app/layout.tsx
    import { SupabaseProvider } from '@/utils/supabase/SupabaseProvider';

    export default function RootLayout({ children }) {
    return (
        <html lang="en">
        <body>
            <SupabaseProvider>
            {children}
            </SupabaseProvider>
        </body>
        </html>
    );
    }
    ```

## Usage

### Client Components (browser)

```tsx
'use client';
import { useSupabase } from '@/utils/supabase/SupabaseProvider';

export default function ProfileComponent() {
  const supabase = useSupabase();
  
  async function handleSignOut() {
    await supabase.auth.signOut();
  }
  
  return <button onClick={handleSignOut}>Sign Out</button>;
}
```

### Server Components (server-side)

```tsx
import { cookies } from 'next/headers';
import { createClient } from '@/utils/supabase/server';

export default async function ServerComponent() {
  const cookieStore = cookies();
  const supabase = createClient(cookieStore);
  
  const { data } = await supabase.from('posts').select('*');
  
  return <div>{JSON.stringify(data)}</div>;
}
```

## Security Considerations

- The anon key is safe to expose in client-side code as it has limited permissions
- For admin operations, use Server Components or API Routes with service role key (never expose this client-side)
- Properly set up Row Level Security (RLS) in your Supabase project
