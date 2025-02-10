#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional
import os
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

from utils.logger import logger

class GoogleSheetsHandler:
    def __init__(self) -> None:
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment
        self.project_id = os.getenv('GOOGLE_SHEETS_PROJECT_ID')
        self.private_key = os.getenv('GOOGLE_SHEETS_PRIVATE_KEY')
        self.client_email = os.getenv('GOOGLE_SHEETS_CLIENT_EMAIL')
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        # Initialize credentials and service
        self.service = self._initialize_service()
        
        # Sheet ranges
        self.ANALYSIS_RANGE = 'Market Analysis!A:F'  # Adjust based on your columns
        
    def _initialize_service(self):
        """Initialize Google Sheets service with credentials"""
        try:
            credentials = {
                "type": "service_account",
                "project_id": self.project_id,
                "private_key": self.private_key.replace('\\n', '\n'),  # Fix newline encoding
                "client_email": self.client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            creds = service_account.Credentials.from_service_account_info(
                credentials, scopes=scopes
            )
            
            service = build('sheets', 'v4', credentials=creds)
            logger.logger.info("Successfully initialized Google Sheets service")
            return service
            
        except Exception as e:
            logger.log_error("Google Sheets Init", f"Failed to initialize service: {str(e)}")
            return None
            
    def write_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Write analysis data to Google Sheets with retry mechanism"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.service:
                    raise Exception("Google Sheets service not initialized")
                
                # Format data for sheet
                row = [
                    analysis_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    analysis_data.get('btc_price', 0),
                    analysis_data.get('eth_price', 0),
                    analysis_data.get('analysis', ''),
                    analysis_data.get('model', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Insert timestamp
                ]
                
                # Prepare the request
                body = {
                    'values': [row]
                }
                
                # Append the row
                result = self.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id,
                    range=self.ANALYSIS_RANGE,
                    valueInputOption='USER_ENTERED',
                    insertDataOption='INSERT_ROWS',
                    body=body
                ).execute()
                
                logger.logger.info(f"Successfully wrote analysis to Google Sheets: {result.get('updates', {}).get('updatedRows', 0)} rows updated")
                return True
                
            except HttpError as e:
                retry_count += 1
                wait_time = retry_count * 10
                logger.logger.warning(f"Google Sheets API error, attempt {retry_count}, waiting {wait_time}s... Error: {str(e)}")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.log_error("Google Sheets Write", f"Failed to write analysis: {str(e)}")
                return False
        
        logger.log_error("Google Sheets Write", "Maximum retries reached")
        return False
        
    def check_connection(self) -> bool:
        """Test connection to Google Sheets"""
        try:
            if not self.service:
                return False
                
            # Try to get sheet metadata
            self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            return True
            
        except Exception as e:
            logger.log_error("Google Sheets Connection", f"Connection test failed: {str(e)}")
            return False
            
    def get_last_analysis(self) -> Optional[Dict[str, Any]]:
        """Get the most recent analysis from the sheet"""
        try:
            if not self.service:
                return None
                
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{self.ANALYSIS_RANGE}!A2:F2",  # Assuming first row is headers
                valueRenderOption='UNFORMATTED_VALUE'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None
                
            # Convert row to dict
            last_row = values[0]
            return {
                'timestamp': last_row[0],
                'btc_price': last_row[1],
                'eth_price': last_row[2],
                'analysis': last_row[3],
                'model': last_row[4],
                'update_time': last_row[5]
            }
            
        except Exception as e:
            logger.log_error("Google Sheets Read", f"Failed to read last analysis: {str(e)}")
            return None

# Create singleton instance
sheets_handler = GoogleSheetsHandler()
