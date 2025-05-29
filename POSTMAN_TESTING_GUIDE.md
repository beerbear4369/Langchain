# Postman Manual Testing Guide for Kuku Coach API

This guide explains how to use the provided Postman collection (`Kuku_Coach_API.postman_collection.json`) to manually test the Kuku Coach API.

## Prerequisites

1.  **Postman Installed**: Download and install Postman from [https://www.postman.com/downloads/](https://www.postman.com/downloads/).
2.  **API Running**: Ensure the Kuku Coach FastAPI application is running locally (e.g., `uvicorn api_main:app --reload` which typically runs on `http://localhost:8000`) or deployed on a server.

## 1. Importing the Collection

1.  Open Postman.
2.  Click on **File** > **Import...** (or click the "Import" button).
3.  Drag and drop the `Kuku_Coach_API.postman_collection.json` file into the import window, or click "Upload Files" and select it.
4.  Confirm the import. You should now see "Kuku Coach API" in your collections list.

## 2. Setting Up Environment Variables

The collection uses variables to make it easy to switch between environments (local, staging, production) and manage dynamic data like session IDs.

1.  **Base URL (`baseUrl`)**:
    *   The collection comes with a `baseUrl` variable pre-set to `http://localhost:8000`.
    *   If your API is running on a different URL (e.g., your Render.com deployed URL), you should update this.
    *   To edit: Click on the "Kuku Coach API" collection, then go to the "Variables" tab. Edit the "CURRENT VALUE" for `baseUrl`.

2.  **Session ID (`sessionId`)**:
    *   This variable is designed to hold the ID of an active session.
    *   It's initially empty. You will populate this after creating a new session.
    *   The collection includes a sample test script in the "Create New Session" request that can automatically set this variable if you uncomment and enable it in the "Tests" tab of that request.
        *   To do this:
            1.  Select the "Create New Session" request.
            2.  Go to its "Tests" tab.
            3.  Uncomment the script:
                ```javascript
                if (pm.request.url.getPath().endsWith('/api/sessions') && pm.request.method === 'POST') {
                    try {
                        const responseJson = pm.response.json();
                        if (responseJson.success && responseJson.data.sessionId) {
                            pm.collectionVariables.set('sessionId', responseJson.data.sessionId);
                            console.log('Set sessionId to:', responseJson.data.sessionId);
                        }
                    } catch (e) {
                        console.log('Error parsing/setting sessionId:', e);
                    }
                }
                ```
            4.  Save the request. Now, after successfully creating a session, `{{sessionId}}` will be automatically populated for other requests.

## 3. Typical Test Flow

Here's a step-by-step guide to testing the core functionality:

### Step 1: Create a New Session

1.  In the "Kuku Coach API" collection, expand the "Session Management" folder.
2.  Select the **"Create New Session"** request.
3.  Ensure the method is `POST` and the URL is `{{baseUrl}}/api/sessions`.
4.  Click **Send**.
5.  **Check the Response**:
    *   **Status Code**: Should be `200 OK`.
    *   **Body**: Should be a JSON response like:
        ```json
        {
            "success": true,
            "data": {
                "sessionId": "some-unique-session-id",
                "createdAt": "timestamp",
                "status": "active"
            }
        }
        ```
6.  **Update `sessionId` Variable**:
    *   If you didn't enable the test script to auto-update, manually copy the `sessionId` value from the response body.
    *   Go to the collection's "Variables" tab and paste it into the "CURRENT VALUE" for the `sessionId` variable.

### Step 2: Send an Audio Message

1.  In the collection, expand the "Conversation" folder.
2.  Select the **"Send Audio Message"** request.
3.  Ensure the method is `POST` and the URL is `{{baseUrl}}/api/sessions/{{sessionId}}/messages`. If `sessionId` is set as a collection variable, Postman will automatically use it.
4.  Go to the **Body** tab and select **form-data**.
5.  You'll see a key named `audio`.
    *   Hover over the `audio` key row, and on the right side, you'll see a dropdown that says "Text". Change this to **"File"**.
    *   A "Select Files" button will appear. Click it and choose an audio file from your computer (e.g., a short `.wav` or `.mp3` file).
6.  Click **Send**.
7.  **Check the Response**:
    *   **Status Code**: Should be `200 OK`.
    *   **Body**: Should contain the transcribed user message and the AI's response, including an `audioUrl` for the AI's spoken response.
        ```json
        {
            "success": true,
            "data": {
                "messages": [
                    {
                        "id": "user-msg-id",
                        "timestamp": "user-msg-timestamp",
                        "sender": "user",
                        "text": "Your transcribed text..."
                    },
                    {
                        "id": "ai-msg-id",
                        "timestamp": "ai-msg-timestamp",
                        "sender": "ai",
                        "text": "AI's response text...",
                        "audioUrl": "/audio/some-ai-audio-file.mp3"
                    }
                ]
            }
        }
        ```
    *   You can try opening the `{{baseUrl}}{{audioUrl}}` in a browser to hear the AI's audio response (e.g., `http://localhost:8000/audio/some-ai-audio-file.mp3`).

### Step 3: Get Conversation History

1.  Select the **"Get Conversation History"** request in the "Conversation" folder.
2.  Ensure the method is `GET` and the URL is `{{baseUrl}}/api/sessions/{{sessionId}}/messages`.
3.  Click **Send**.
4.  **Check the Response**:
    *   **Status Code**: Should be `200 OK`.
    *   **Body**: Should be a JSON array containing all messages exchanged so far in the session.

### Step 4: Get Session Status (Optional)

1.  Select the **"Get Session Status"** request in the "Session Management" folder.
2.  Ensure the method is `GET` and the URL is `{{baseUrl}}/api/sessions/{{sessionId}}`.
3.  Click **Send**.
4.  **Check the Response**:
    *   **Status Code**: Should be `200 OK`.
    *   **Body**: Should show session details, including an updated `messageCount`.

### Step 5: End Session

1.  Select the **"End Session"** request in the "Session Management" folder.
2.  Ensure the method is `POST` and the URL is `{{baseUrl}}/api/sessions/{{sessionId}}/end`.
3.  Click **Send**.
4.  **Check the Response**:
    *   **Status Code**: Should be `200 OK`.
    *   **Body**: Should contain the session summary.

## Troubleshooting

*   **`Could not get any response`**: Make sure your API application is running and accessible at the `baseUrl`.
*   **`404 Not Found` for `{{sessionId}}` requests**: Double-check that `sessionId` was correctly copied and set in the collection variables, or that the auto-set script ran successfully.
*   **Authentication Errors (Future)**: If authentication is added to the API, you'll need to configure Postman to send the required authentication headers (e.g., API keys, tokens).

This guide should help you get started with testing the Kuku Coach API using Postman!
```
