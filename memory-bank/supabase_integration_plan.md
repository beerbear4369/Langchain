# Kuku Coach Supabase Integration Plan

## Overview

This document outlines the step-by-step plan to integrate Supabase as the persistent database for Kuku Coach, following best practices for a backend-driven architecture. The frontend will **only communicate with the backend API**; all Supabase operations are handled by the backend. Audio files remain temporary and are not stored in Supabase.

---

## Phase 1: Basic Database Storage (Backend-Only Integration)

### 1.1 Database Schema (No Audio Storage)

```sql
-- Sessions table
CREATE TABLE public.sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id TEXT UNIQUE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- For future auth
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'ended')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  message_count INTEGER DEFAULT 0,
  summary TEXT,
  duration_seconds INTEGER,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  feedback TEXT
);

-- Messages table (no audio storage)
CREATE TABLE public.messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
  message_id TEXT UNIQUE NOT NULL,
  sender TEXT NOT NULL CHECK (sender IN ('user', 'ai')),
  text_content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_sessions_session_id ON public.sessions(session_id);
CREATE INDEX idx_sessions_user_id ON public.sessions(user_id);
CREATE INDEX idx_messages_session_id ON public.messages(session_id);
CREATE INDEX idx_messages_text_content ON public.messages USING gin(to_tsvector('english', text_content));

-- Enable RLS (allow all for now)
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Temporary policies (no auth yet)
CREATE POLICY "Allow all operations on sessions" ON public.sessions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on messages" ON public.messages FOR ALL USING (true) WITH CHECK (true);
```

---

### 1.2 Backend Database Service (Python)

- Use the `supabase-py` client with the **service role key** for backend operations.
- Implement a `DatabaseService` class to handle all session and message persistence.
- All audio files remain temporary and are served from `/audio/` as before.

**Key Methods:**
- `create_session(session_id, user_id=None)`
- `get_session(session_id)`
- `update_session(session_id, updates)`
- `end_session(session_id, summary, duration, rating=None, feedback=None)`
- `save_message(session_id, message_id, sender, text_content)`
- `get_conversation_history(session_id)`
- `search_messages_global(query, user_id=None)`

---

### 1.3 Backend API Changes

- On session creation, persist to Supabase and keep in-memory for active use.
- On message send, save both user and AI messages to Supabase.
- On session end, update status and summary in Supabase.
- Add endpoints for:
  - **Global search**: `/api/search/messages?q=...&user_id=...`
  - **Session rating**: `/api/sessions/{session_id}/rate`
  - **Conversation history**: `/api/sessions/{session_id}/messages` (now reads from Supabase)
- **No changes to frontend**: All API contracts remain the same.
- **No persistent audio storage**: Audio files are still temporary and served via `/audio/`.

---

### 1.4 Environment Variables

```env
# Backend .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Frontend .env.local (no changes needed)
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## Phase 2: Future Authentication Integration

- Update RLS policies to filter by `auth.uid()`.
- Add user management in backend.
- Modify search to be user-specific.
- Frontend remains unchanged (still only talks to backend API).

---

## Phase 3: Search Implementation

- Use PostgreSQL full-text search for global message search.
- Search endpoint returns all matching messages for a user across all sessions.

---

## Summary

- **Frontend**: No changes required; continues to use backend API only.
- **Backend**: Adds Supabase persistence for sessions and messages, search, and rating endpoints.
- **Audio**: Remains temporary, not stored in Supabase.
- **Scalability**: Ready for future authentication and advanced features.

---

## Development Checklist

- [ ] Create Supabase tables and indexes as above
- [ ] Implement `DatabaseService` in backend
- [ ] Update backend endpoints to persist and retrieve data from Supabase
- [ ] Test all endpoints for compatibility with frontend
- [ ] Plan for future authentication and search improvements

---

**This plan ensures a smooth, phase-by-phase migration to Supabase, with zero disruption to the frontend and a clear path for future enhancements.** 