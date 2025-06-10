# System Patterns: Kuku Coach API

## 1. Overall Architecture: Stateless API with Simulated State

The system is designed as a stateless API built on FastAPI. While the HTTP protocol is stateless, the application simulates a stateful conversation by using a server-side session store.

*   **Pattern:** State Simulation via Token (`session_id`).
*   **Implementation:** Every conversation is assigned a unique `session_id`. The client must include this `session_id` in every request. The server uses this ID to retrieve the complete context for that conversation (e.g., message history, timestamps) from its session store before processing the request.

## 2. Session State Management

*   **Pattern:** In-Memory Dictionary Store.
*   **Implementation:** The `app.py` script uses a global dictionary (`sessions`) to store all active session data. The key is the `session_id`, and the value is another dictionary containing all session attributes (`createdAt`, `messageCount`, `awaitingWrapUpConfirmation`, etc.).
*   **Limitation:** This approach is not persistent. If the server restarts, all active sessions are lost. This is acceptable for development but will be replaced by a database-backed store for production.

## 3. Conversation Logic Flow

*   **Pattern:** Prioritized Conditional Logic for User Intent.
*   **Implementation:** The primary message processing endpoint (`/api/sessions/{session_id}/messages`) uses a strict order of operations to interpret the user's intent, preventing ambiguity.
    1.  **Check for Confirmation First:** The highest priority is to check if the session is in an `awaitingWrapUpConfirmation` state. If it is, the user's message is processed as a confirmation or rejection, and the flow stops there.
    2.  **Check for New Wrap-Up Request:** If not awaiting confirmation, the system then checks if the message is a *new* request to initiate a wrap-up.
    3.  **Default to Normal Processing:** If neither of the above conditions is met, the message is treated as a standard part of the ongoing conversation.
*   **Significance:** This pattern was established to fix a critical bug where a confirmation message containing wrap-up keywords was being misinterpreted as a new wrap-up request, leading to a loop.

## 4. Time and Turn Tracking

*   **Pattern:** On-Demand Calculation from Stored State.
*   **Implementation:** The system avoids storing and constantly updating "elapsed time" or "turn count." Instead, it stores foundational data and calculates these values when needed.
    *   **Elapsed Time:** Calculated by subtracting the stored `createdAt` timestamp from the current request's timestamp.
    *   **Turn Count:** Calculated by dividing the stored `messageCount` by two.
*   **Benefit:** This is an efficient pattern for a stateless environment, as it minimizes the amount of data that needs to be updated and stored with each request. 