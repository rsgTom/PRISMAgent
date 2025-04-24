// supabase client for browser-side usage
import { createBrowserClient } from '@supabase/ssr';

/**
 * Creates a Supabase client for client-side (browser) usage
 * 
 * @returns A Supabase client instance
 */
export const createClient = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
  
  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('Supabase environment variables are not properly set');
  }
  
  return createBrowserClient(supabaseUrl, supabaseAnonKey);
}; 