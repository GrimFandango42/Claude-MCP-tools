"""Zettelkasten knowledge management system.

Implements a notes-based knowledge management system inspired by the
Zettelkasten method with linking, tagging, and search capabilities.
"""

import logging
import re
from datetime import datetime

logger = logging.getLogger('knowledge-memory-mcp.zettelkasten')

class ZettelkastenManager:
    """Manager for Zettelkasten-style notes system."""
    
    def __init__(self, db):
        """Initialize the ZettelkastenManager.
        
        Args:
            db: Database instance for storage
        """
        self.db = db
        logger.info("Zettelkasten manager initialized")
    
    def create_note(self, title, content, tags=None):
        """Create a new note with optional tags.
        
        Args:
            title: Note title
            content: Note content text
            tags: List of tag names (optional)
            
        Returns:
            str: ID of the created note
        """
        note_id = self.db.generate_id()
        
        # Insert note
        self.db.execute(
            "INSERT INTO notes (id, title, content) VALUES (?, ?, ?)",
            (note_id, title, content)
        )
        
        # Process tags if provided
        if tags:
            self._add_tags_to_note(note_id, tags)
            
        # Extract and link references
        self.extract_and_link_references(note_id)
        
        self.db.commit()
        return note_id
    
    def get_note(self, note_id):
        """Get a note by its ID.
        
        Args:
            note_id: The note's unique ID
            
        Returns:
            dict: Note data including title, content, tags, and metadata
        """
        # Get basic note data
        cursor = self.db.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?", 
            (note_id,)
        )
        note = cursor.fetchone()
        
        if not note:
            return None
            
        # Convert to dict
        note_dict = dict(note)
        
        # Get tags
        cursor = self.db.execute(
            """SELECT t.name FROM tags t
               JOIN note_tags nt ON t.id = nt.tag_id
               WHERE nt.note_id = ?""",
            (note_id,)
        )
        tags = [row['name'] for row in cursor.fetchall()]
        note_dict['tags'] = tags
        
        return note_dict
    
    def update_note(self, note_id, title=None, content=None, tags=None):
        """Update an existing note.
        
        Args:
            note_id: The note's unique ID
            title: New title (optional)
            content: New content (optional)
            tags: New list of tags (optional)
            
        Returns:
            bool: True if update was successful
        """
        # Check if note exists
        cursor = self.db.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            return False
            
        update_parts = []
        params = []
        
        if title is not None:
            update_parts.append("title = ?")
            params.append(title)
            
        if content is not None:
            update_parts.append("content = ?")
            params.append(content)
        
        if update_parts:
            update_parts.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE notes SET {', '.join(update_parts)} WHERE id = ?"
            params.append(note_id)
            self.db.execute(query, params)
        
        # Update tags if provided
        if tags is not None:
            # Remove existing tags
            self.db.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
            # Add new tags
            self._add_tags_to_note(note_id, tags)
        
        # Re-extract and link references if content was updated
        if content is not None:
            # Remove existing links where this note is the source
            self.db.execute("DELETE FROM note_links WHERE source_id = ?", (note_id,))
            # Re-extract and create links
            self.extract_and_link_references(note_id)
        
        self.db.commit()
        return True
    
    def delete_note(self, note_id):
        """Delete a note by its ID.
        
        Args:
            note_id: The note's unique ID
            
        Returns:
            bool: True if deletion was successful
        """
        cursor = self.db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        success = cursor.rowcount > 0
        self.db.commit()
        return success
    
    def search_notes(self, query, limit=10):
        """Search notes by title and content.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            list: Matching notes with metadata
        """
        cursor = self.db.execute(
            """SELECT id, title, substr(content, 1, 150) as snippet, created_at 
               FROM notes 
               WHERE title LIKE ? OR content LIKE ? 
               ORDER BY updated_at DESC 
               LIMIT ?""",
            (f'%{query}%', f'%{query}%', limit)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_tags(self):
        """Get all tags in the knowledge base.
        
        Returns:
            list: All tag names
        """
        cursor = self.db.execute("SELECT name FROM tags ORDER BY name")
        return [row['name'] for row in cursor.fetchall()]
    
    def search_notes_by_tag(self, tag, limit=10):
        """Search notes by tag.
        
        Args:
            tag: Tag name to search for
            limit: Maximum number of results
            
        Returns:
            list: Notes with the specified tag
        """
        cursor = self.db.execute(
            """SELECT n.id, n.title, substr(n.content, 1, 150) as snippet, n.created_at 
               FROM notes n
               JOIN note_tags nt ON n.id = nt.note_id
               JOIN tags t ON nt.tag_id = t.id
               WHERE t.name = ?
               ORDER BY n.updated_at DESC
               LIMIT ?""",
            (tag, limit)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_backlinks(self, note_id):
        """Get all notes that link to the specified note.
        
        Args:
            note_id: The note's unique ID
            
        Returns:
            list: Notes that link to the specified note
        """
        cursor = self.db.execute(
            """SELECT n.id, n.title 
               FROM notes n
               JOIN note_links nl ON n.id = nl.source_id
               WHERE nl.target_id = ?
               ORDER BY n.updated_at DESC""",
            (note_id,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def extract_and_link_references(self, note_id):
        """Extract references from a note and create links.
        
        Looks for [[note-id]] patterns in content and creates links.
        
        Args:
            note_id: The note's unique ID
            
        Returns:
            dict: Information about extracted links
        """
        cursor = self.db.execute("SELECT content FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        
        if not note:
            return {"error": "Note not found"}
            
        content = note['content']
        
        # Find references in format [[note-id]]
        pattern = r'\[\[([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\]\]'
        references = re.findall(pattern, content)
        
        # Create links for valid references
        created_links = 0
        for ref_id in references:
            # Check if referenced note exists
            cursor = self.db.execute("SELECT id FROM notes WHERE id = ?", (ref_id,))
            if cursor.fetchone():
                # Create link if it doesn't already exist
                link_id = self.db.generate_id()
                try:
                    self.db.execute(
                        "INSERT INTO note_links (id, source_id, target_id) VALUES (?, ?, ?)",
                        (link_id, note_id, ref_id)
                    )
                    created_links += 1
                except Exception:
                    # Link may already exist or other constraint violation
                    pass
        
        self.db.commit()
        return {
            "links_found": len(references),
            "links_created": created_links
        }
    
    def get_recent_notes(self, limit=10):
        """Get recently updated notes.
        
        Args:
            limit: Maximum number of notes to return
            
        Returns:
            list: Recently updated notes
        """
        cursor = self.db.execute(
            """SELECT id, title, substr(content, 1, 150) as snippet, updated_at 
               FROM notes 
               ORDER BY updated_at DESC 
               LIMIT ?""",
            (limit,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_note_count(self):
        """Get the total number of notes.
        
        Returns:
            int: Total note count
        """
        cursor = self.db.execute("SELECT COUNT(*) as count FROM notes")
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def get_link_count(self):
        """Get the total number of links.
        
        Returns:
            int: Total link count
        """
        cursor = self.db.execute("SELECT COUNT(*) as count FROM note_links")
        result = cursor.fetchone()
        return result['count'] if result else 0
        
    def _add_tags_to_note(self, note_id, tags):
        """Add tags to a note.
        
        Args:
            note_id: The note's unique ID
            tags: List of tag names
        """
        for tag_name in tags:
            # Get or create tag
            cursor = self.db.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag = cursor.fetchone()
            
            if tag:
                tag_id = tag['id']
            else:
                tag_id = self.db.generate_id()
                self.db.execute(
                    "INSERT INTO tags (id, name) VALUES (?, ?)",
                    (tag_id, tag_name)
                )
            
            # Add tag to note
            try:
                self.db.execute(
                    "INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)",
                    (note_id, tag_id)
                )
            except Exception:
                # Tag may already be associated with note
                pass