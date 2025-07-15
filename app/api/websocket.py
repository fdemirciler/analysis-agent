import asyncio
import json
import base64
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from app.core.session import SessionManager
import pandas as pd

class WebSocketAPI:
    """WebSocket API for real-time communication with the client"""
    
    def __init__(self, app: FastAPI, orchestrator, session_manager: SessionManager):
        self.app = app
        self.orchestrator = orchestrator
        self.session_manager = session_manager
        
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            session_id = self.session_manager.create_session(websocket)
            
            try:
                # Send session ID to client
                await websocket.send_json({
                    "type": "session_created",
                    "session_id": session_id
                })
                
                while True:
                    message = await websocket.receive_json()
                    await self._handle_message(session_id, message)
                    
            except WebSocketDisconnect:
                self.session_manager.end_session(session_id)
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"An unexpected error occurred: {str(e)}"
                })
                self.session_manager.end_session(session_id)
    
    async def _handle_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming WebSocket messages"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return
            
        websocket = session["websocket"]
        message_type = message.get("type")
        
        if message_type == "file_upload":
            # Process file upload
            file_data = message.get("data")
            file_name = message.get("file_name")
            
            # Create temp directory if it doesn't exist
            os.makedirs("temp", exist_ok=True)
            file_path = f"temp/{session_id}_{file_name}"
            
            # Save file data to temporary file
            try:
                # Decode base64 data if needed
                if isinstance(file_data, str) and file_data.startswith('data:'):
                    header, encoded = file_data.split(",", 1)
                    file_data = base64.b64decode(encoded)
                
                with open(file_path, "wb") as f:
                    if isinstance(file_data, str):
                        f.write(file_data.encode('utf-8'))
                    else:
                        f.write(file_data)
                
                # Update client on progress
                await websocket.send_json({
                    "type": "processing_status",
                    "status": "Processing file...",
                    "progress": 0.1
                })
                
                # Process file with orchestrator
                data_profile, dataframe = await self.orchestrator.process_file(file_path, file_name)
                
                # Store in session
                self.session_manager.update_session_data(session_id, "data_profile", data_profile)
                self.session_manager.update_session_data(session_id, "dataframe", dataframe)
                self.session_manager.update_session_data(session_id, "file_name", file_name)
                
                # Send success response
                await websocket.send_json({
                    "type": "file_processed",
                    "profile_summary": {
                        "file_name": file_name,
                        "rows": data_profile["row_count"],
                        "columns": data_profile["column_count"],
                        "periods": data_profile["periods"]
                    }
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing file: {str(e)}"
                })
                
        elif message_type == "query":
            # Process user query
            query = message.get("query")
            
            # Check if file is uploaded
            if session["dataframe"] is None or session["data_profile"] is None:
                await websocket.send_json({
                    "type": "error",
                    "message": "Please upload a file first."
                })
                return
                
            try:
                # Send thinking status
                await websocket.send_json({
                    "type": "processing_status",
                    "status": "Analyzing your query...",
                    "progress": 0.3
                })
                
                # Process query with orchestrator
                response = await self.orchestrator.process_query(
                    query, 
                    session["data_profile"], 
                    session["dataframe"],
                    session["conversation_history"]
                )
                
                # Reset retry counter on success
                self.session_manager.reset_retry_count(session_id)
                
                # Add to conversation history
                self.session_manager.add_to_conversation(session_id, {
                    "role": "user",
                    "content": query
                })
                self.session_manager.add_to_conversation(session_id, {
                    "role": "assistant",
                    "content": response
                })
                
                # Send response
                await websocket.send_json({
                    "type": "query_response",
                    "response": response
                })
                
            except Exception as e:
                # Increment retry counter
                retry_count = self.session_manager.increment_retry_count(session_id)
                
                # Check if max retries reached
                if retry_count >= 5:
                    await websocket.send_json({
                        "type": "error",
                        "message": "I'm having trouble understanding your question or analyzing this data. Please try reformulating your question or uploading a different file."
                    })
                    self.session_manager.reset_retry_count(session_id)
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing query (attempt {retry_count}/5): {str(e)}"
                    })