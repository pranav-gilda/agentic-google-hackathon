"""
SQLite Database Module for Story Storage
Stores stories, runs, and metadata for persistence and analytics.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class StoryDatabase:
    """SQLite database for storing stories and generation runs."""
    
    def __init__(self, db_path: str = "stories.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Stories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_request TEXT NOT NULL,
                story_text TEXT NOT NULL,
                model_used TEXT NOT NULL,
                judge_score REAL NOT NULL,
                revision_count INTEGER NOT NULL,
                meets_quality_threshold INTEGER NOT NULL,
                mcp_enabled INTEGER NOT NULL,
                fallback_used INTEGER NOT NULL,
                storyteller_temperature REAL,
                judge_temperature REAL,
                max_story_tokens INTEGER,
                quality_threshold REAL,
                max_revisions INTEGER,
                judge_feedback TEXT,
                parent_settings TEXT,
                tool_calls TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Runs table for tracking generation attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_request TEXT NOT NULL,
                success INTEGER NOT NULL,
                model_used TEXT,
                error_message TEXT,
                generation_time_seconds REAL,
                mcp_enabled INTEGER,
                fallback_used INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stories_timestamp ON stories(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stories_model ON stories(model_used)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def save_story(self, story_data: Dict) -> int:
        """
        Save a generated story to the database.
        
        Args:
            story_data: Dictionary containing story information
            
        Returns:
            Story ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = story_data.get('timestamp', datetime.now().isoformat())
        
        cursor.execute("""
            INSERT INTO stories (
                timestamp, user_request, story_text, model_used, judge_score,
                revision_count, meets_quality_threshold, mcp_enabled, fallback_used,
                storyteller_temperature, judge_temperature, max_story_tokens,
                quality_threshold, max_revisions, judge_feedback, parent_settings, tool_calls
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            story_data.get('user_request', ''),
            story_data.get('story', ''),
            story_data.get('model_used', 'unknown'),
            story_data.get('judge_score', 0.0),
            story_data.get('revision_count', 0),
            1 if story_data.get('meets_quality_threshold', False) else 0,
            1 if story_data.get('mcp_enabled', False) else 0,
            1 if story_data.get('fallback_used', False) else 0,
            story_data.get('storyteller_temperature'),
            story_data.get('judge_temperature'),
            story_data.get('max_story_tokens'),
            story_data.get('quality_threshold'),
            story_data.get('max_revisions'),
            story_data.get('judge_feedback', ''),
            json.dumps(story_data.get('parent_settings', {})),
            json.dumps(story_data.get('tool_calls', []))
        ))
        
        story_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return story_id
    
    def save_run(self, run_data: Dict) -> int:
        """
        Save a generation run (success or failure) to the database.
        
        Args:
            run_data: Dictionary containing run information
            
        Returns:
            Run ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = run_data.get('timestamp', datetime.now().isoformat())
        
        cursor.execute("""
            INSERT INTO runs (
                timestamp, user_request, success, model_used, error_message,
                generation_time_seconds, mcp_enabled, fallback_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            run_data.get('user_request', ''),
            1 if run_data.get('success', False) else 0,
            run_data.get('model_used'),
            run_data.get('error_message'),
            run_data.get('generation_time_seconds'),
            1 if run_data.get('mcp_enabled', False) else 0,
            1 if run_data.get('fallback_used', False) else 0
        ))
        
        run_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return run_id
    
    def get_all_stories(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all stories from the database.
        
        Args:
            limit: Optional limit on number of stories to return
            
        Returns:
            List of story dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM stories ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        stories = []
        for row in rows:
            story = dict(row)
            # Convert JSON strings back to objects
            if story.get('parent_settings'):
                try:
                    story['parent_settings'] = json.loads(story['parent_settings'])
                except:
                    story['parent_settings'] = {}
            if story.get('tool_calls'):
                try:
                    story['tool_calls'] = json.loads(story['tool_calls'])
                except:
                    story['tool_calls'] = []
            # Convert boolean fields
            story['meets_quality_threshold'] = bool(story['meets_quality_threshold'])
            story['mcp_enabled'] = bool(story['mcp_enabled'])
            story['fallback_used'] = bool(story['fallback_used'])
            # Rename story_text to story for consistency
            story['story'] = story.pop('story_text', '')
            stories.append(story)
        
        conn.close()
        return stories
    
    def get_story_by_id(self, story_id: int) -> Optional[Dict]:
        """
        Retrieve a specific story by ID.
        
        Args:
            story_id: Story ID
            
        Returns:
            Story dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        
        if row:
            story = dict(row)
            # Convert JSON strings back to objects
            if story.get('parent_settings'):
                try:
                    story['parent_settings'] = json.loads(story['parent_settings'])
                except:
                    story['parent_settings'] = {}
            if story.get('tool_calls'):
                try:
                    story['tool_calls'] = json.loads(story['tool_calls'])
                except:
                    story['tool_calls'] = []
            # Convert boolean fields
            story['meets_quality_threshold'] = bool(story['meets_quality_threshold'])
            story['mcp_enabled'] = bool(story['mcp_enabled'])
            story['fallback_used'] = bool(story['fallback_used'])
            # Rename story_text to story for consistency
            story['story'] = story.pop('story_text', '')
            conn.close()
            return story
        
        conn.close()
        return None
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total stories
        cursor.execute("SELECT COUNT(*) FROM stories")
        total_stories = cursor.fetchone()[0]
        
        # Total runs
        cursor.execute("SELECT COUNT(*) FROM runs")
        total_runs = cursor.fetchone()[0]
        
        # Successful runs
        cursor.execute("SELECT COUNT(*) FROM runs WHERE success = 1")
        successful_runs = cursor.fetchone()[0]
        
        # Average judge score
        cursor.execute("SELECT AVG(judge_score) FROM stories")
        avg_score = cursor.fetchone()[0] or 0.0
        
        # Stories by model
        cursor.execute("""
            SELECT model_used, COUNT(*) as count 
            FROM stories 
            GROUP BY model_used
        """)
        model_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # MCP usage
        cursor.execute("SELECT COUNT(*) FROM stories WHERE mcp_enabled = 1")
        mcp_stories = cursor.fetchone()[0]
        
        # Fallback usage
        cursor.execute("SELECT COUNT(*) FROM stories WHERE fallback_used = 1")
        fallback_stories = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_stories': total_stories,
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': total_runs - successful_runs,
            'average_judge_score': round(avg_score, 2),
            'stories_by_model': model_counts,
            'mcp_enabled_count': mcp_stories,
            'fallback_used_count': fallback_stories
        }
    
    def delete_story(self, story_id: int) -> bool:
        """
        Delete a story by ID.
        
        Args:
            story_id: Story ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM stories WHERE id = ?", (story_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_all_stories(self):
        """Clear all stories from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM stories")
        cursor.execute("DELETE FROM runs")
        
        conn.commit()
        conn.close()

