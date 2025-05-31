// MongoDB initialization script for PromptAchat

/* eslint-disable no-undef */

// Create database and user
db = db.getSiblingDB('promptachat_db');

// Create application user
db.createUser({
  user: 'promptachat_user',
  pwd: 'promptachat_app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'promptachat_db'
    }
  ]
});

// Create initial collections with indexes
db.createCollection('users');
db.createCollection('prompts');
db.createCollection('files');
db.createCollection('sessions');

// User indexes
db.users.createIndex({ "uid": 1 }, { unique: true });
db.users.createIndex({ "email": 1 });

// Prompt indexes
db.prompts.createIndex({ "created_by": 1 });
db.prompts.createIndex({ "category": 1 });
db.prompts.createIndex({ "type": 1 });

// File indexes
db.files.createIndex({ "uploaded_by": 1 });
db.files.createIndex({ "uploaded_at": 1 });

// Session indexes
db.sessions.createIndex({ "user_id": 1 });
db.sessions.createIndex({ "created_at": 1 }, { expireAfterSeconds: 3600 });

print('MongoDB initialization completed for PromptAchat');