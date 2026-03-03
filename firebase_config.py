"""
Firebase configuration and initialization for Knowledge Graph persistence.
Uses Firestore for document storage of nodes and relationships.
"""
import os
from typing import Optional
import logging
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client as FirestoreClient
from google.api_core.exceptions import GoogleAPIError

class FirebaseConfig:
    """Singleton configuration manager for Firebase"""
    
    _instance: Optional['FirebaseConfig'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._app = None
            self._db: Optional[FirestoreClient] = None
            self._initialized = True
    
    def initialize(self, credential_path: Optional[str] = None, 
                  project_id: Optional[str] = None) -> FirestoreClient:
        """
        Initialize Firebase connection with robust error handling
        
        Args:
            credential_path: Path to service account key file
            project_id: Firebase project ID
            
        Returns:
            Firestore client instance
            
        Raises:
            FileNotFoundError: If credential file doesn't exist
            GoogleAPIError: If Firebase initialization fails
        """
        try:
            # Check for environment variable first
            if os.environ.get('USE_FIREBASE_EMULATOR', 'false').lower() == 'true':
                os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
                credentials_obj = credentials.ApplicationDefault()
                self._app = firebase_admin.initialize_app(credentials_obj, {
                    'projectId': project_id or 'knowledge-graph-local'
                })
                logging.info("Using Firestore emulator")
            else:
                # Check credential file exists
                if credential_path and not Path(credential_path).exists():
                    raise FileNotFoundError(f"Credential file not found: {credential_path}")
                
                # Use provided path or environment variable
                cred_path = credential_path or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if not cred_path:
                    raise ValueError("No Firebase credentials provided. Set GOOGLE_APPLICATION_CREDENTIALS env var.")
                
                credentials_obj = credentials.Certificate(cred_path)
                self._app = firebase_admin.initialize_app(credentials_obj)
                logging.info("Firebase Admin initialized successfully")
            
            # Initialize Firestore client
            self._db = firestore.client()
            
            # Test connection
            test_doc = self._db.collection('_test').document('connection')
            test_doc.set({'timestamp': firestore.SERVER_TIMESTAMP})
            test_doc.delete()
            
            logging.info("Firestore connection established and tested")
            return self._db
            
        except GoogleAPIError as e:
            logging.error(f"Firebase API error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    @property
    def db(self) -> FirestoreClient:
        """Get Firestore client instance"""
        if self._db is None:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self._db
    
    def cleanup(self):
        """Clean up Firebase resources"""
        if self._app:
            firebase_admin.delete_app(self._app)
            self._app = None
            self._db = None
            logging.info("Firebase resources cleaned up")