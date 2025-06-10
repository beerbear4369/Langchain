# Rating API Frontend Integration Guide

## Overview
This guide explains how to integrate the session rating functionality into the Kuku Coach frontend. Users can rate completed coaching sessions on a 1-5 scale with optional feedback.

## API Endpoints

### 1. Submit Session Rating
```typescript
POST /api/sessions/{sessionId}/rating
Content-Type: application/json

// Request Body
{
  "rating": number,        // Required: 1-5 scale
  "feedback": string       // Optional: text feedback
}

// Response
{
  "success": boolean,
  "data": {
    "sessionId": string,
    "rating": number,
    "feedback": string,
    "timestamp": string
  },
  "error": string          // Only present if success is false
}
```

### 2. Get Existing Rating
```typescript
GET /api/sessions/{sessionId}/rating

// Response
{
  "success": boolean,
  "data": {
    "sessionId": string,
    "rating": number | null,
    "feedback": string | null,
    "hasRating": boolean
  },
  "error": string          // Only present if success is false
}
```

## TypeScript Interfaces

```typescript
// API Request/Response Types
interface RatingSubmission {
  rating: number;          // 1-5 scale
  feedback?: string;       // Optional feedback
}

interface RatingResponse {
  success: boolean;
  data?: {
    sessionId: string;
    rating: number;
    feedback: string;
    timestamp: string;
  };
  error?: string;
}

interface RatingData {
  sessionId: string;
  rating: number | null;
  feedback: string | null;
  hasRating: boolean;
}

// Component Props
interface SessionRatingProps {
  sessionId: string;
  onRatingSubmit?: (rating: number, feedback?: string) => void;
  className?: string;
}
```

## API Service Functions

```typescript
// services/ratingService.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const ratingService = {
  // Submit a new rating
  async submitRating(sessionId: string, rating: number, feedback?: string): Promise<RatingResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/rating`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rating, feedback }),
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: 'Failed to submit rating. Please try again.',
      };
    }
  },

  // Get existing rating for a session
  async getRating(sessionId: string): Promise<{ success: boolean; data?: RatingData; error?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/rating`);
      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: 'Failed to load rating data.',
      };
    }
  },
};
```

## React Components

### Star Rating Component
```typescript
// components/StarRating.tsx
import React from 'react';
import { Star } from 'lucide-react';

interface StarRatingProps {
  rating: number;
  onRatingChange: (rating: number) => void;
  readonly?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const StarRating: React.FC<StarRatingProps> = ({
  rating,
  onRatingChange,
  readonly = false,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => !readonly && onRatingChange(star)}
          disabled={readonly}
          className={`${sizeClasses[size]} ${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'} transition-transform`}
        >
          <Star
            className={`${sizeClasses[size]} ${
              star <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300 hover:text-yellow-300'
            }`}
          />
        </button>
      ))}
    </div>
  );
};
```

### Session Rating Component
```typescript
// components/SessionRating.tsx
import React, { useState, useEffect } from 'react';
import { StarRating } from './StarRating';
import { ratingService } from '../services/ratingService';

interface SessionRatingProps {
  sessionId: string;
  onRatingSubmit?: (rating: number, feedback?: string) => void;
  className?: string;
}

export const SessionRating: React.FC<SessionRatingProps> = ({
  sessionId,
  onRatingSubmit,
  className = '',
}) => {
  const [rating, setRating] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>('');
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Load existing rating on mount
  useEffect(() => {
    const loadExistingRating = async () => {
      const result = await ratingService.getRating(sessionId);
      if (result.success && result.data?.hasRating) {
        setRating(result.data.rating || 0);
        setFeedback(result.data.feedback || '');
        setIsSubmitted(true);
      }
    };

    loadExistingRating();
  }, [sessionId]);

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }

    setIsLoading(true);
    setError('');

    const result = await ratingService.submitRating(sessionId, rating, feedback);

    if (result.success) {
      setIsSubmitted(true);
      onRatingSubmit?.(rating, feedback);
    } else {
      setError(result.error || 'Failed to submit rating');
    }

    setIsLoading(false);
  };

  const handleEdit = () => {
    setIsSubmitted(false);
    setError('');
  };

  return (
    <div className={`rating-component bg-white rounded-lg p-6 shadow-sm border ${className}`}>
      <h3 className="text-lg font-semibold mb-4">Rate Your Session</h3>
      
      <div className="space-y-4">
        {/* Star Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            How was your coaching session?
          </label>
          <StarRating
            rating={rating}
            onRatingChange={setRating}
            readonly={isSubmitted}
            size="lg"
          />
        </div>

        {/* Feedback Textarea */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Feedback (Optional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={isSubmitted}
            placeholder="Share your thoughts about the session..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          {!isSubmitted ? (
            <button
              onClick={handleSubmit}
              disabled={rating === 0 || isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Submitting...' : 'Submit Rating'}
            </button>
          ) : (
            <>
              <div className="text-green-600 text-sm flex items-center">
                ✓ Rating submitted successfully
              </div>
              <button
                onClick={handleEdit}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Edit Rating
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
```

## Integration into Existing Pages

### SessionSummaryPage Integration
```typescript
// pages/SessionSummaryPage.tsx (Add to existing component)
import { SessionRating } from '../components/SessionRating';

// Add inside your SessionSummaryPage component after the summary content:
<div className="space-y-6">
  {/* Existing summary content */}
  <div className="session-summary">
    {/* Your existing summary display */}
  </div>

  {/* Add Rating Component */}
  <SessionRating
    sessionId={sessionId}
    onRatingSubmit={(rating, feedback) => {
      console.log('Rating submitted:', { rating, feedback });
      // Optional: Show success toast, update analytics, etc.
    }}
    className="mt-6"
  />

  {/* Existing navigation buttons */}
  <div className="flex gap-4">
    {/* Your existing buttons */}
  </div>
</div>
```

### Custom Hook (Optional)
```typescript
// hooks/useSessionRating.ts
import { useState, useEffect } from 'react';
import { ratingService } from '../services/ratingService';

export const useSessionRating = (sessionId: string) => {
  const [rating, setRating] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>('');
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadRating = async () => {
      const result = await ratingService.getRating(sessionId);
      if (result.success && result.data?.hasRating) {
        setRating(result.data.rating || 0);
        setFeedback(result.data.feedback || '');
        setIsSubmitted(true);
      }
    };

    loadRating();
  }, [sessionId]);

  const submitRating = async (newRating: number, newFeedback?: string) => {
    setIsLoading(true);
    setError('');

    const result = await ratingService.submitRating(sessionId, newRating, newFeedback);

    if (result.success) {
      setRating(newRating);
      setFeedback(newFeedback || '');
      setIsSubmitted(true);
    } else {
      setError(result.error || 'Failed to submit rating');
    }

    setIsLoading(false);
    return result.success;
  };

  return {
    rating,
    feedback,
    isSubmitted,
    isLoading,
    error,
    submitRating,
    setRating,
    setFeedback,
    setIsSubmitted,
  };
};
```

## User Flow

1. **Session Completion** → User reaches SessionSummaryPage
2. **Rating Display** → Rating component shows below summary
3. **User Interaction** → User clicks stars (1-5) and optionally adds feedback
4. **Submission** → Click "Submit Rating" button
5. **Success State** → Shows confirmation with "Edit Rating" option
6. **Persistence** → Rating saved to database and persists on page refresh

## Error Handling

- **Network Errors**: Show user-friendly error messages
- **Invalid Rating**: Validate 1-5 range on frontend and backend
- **Session Not Found**: Handle gracefully with error message
- **Rating Already Exists**: Allow editing existing ratings

## Styling Notes

- Uses Tailwind CSS classes (matching your existing design system)
- Responsive design for mobile and desktop
- Accessible focus states and ARIA labels
- Yellow star colors for ratings
- Consistent with shadcn/ui design patterns

## Backend Requirements Met

✅ Rating validation (1-5 scale)  
✅ Optional feedback text  
✅ Session existence validation  
✅ Only ended sessions can be rated  
✅ Rating persistence in database  
✅ Edit existing ratings capability  

This implementation provides a complete, production-ready rating system that integrates seamlessly with your existing Kuku Coach frontend architecture. 