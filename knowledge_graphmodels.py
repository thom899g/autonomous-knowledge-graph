"""
Data models for Knowledge Graph with Pydantic validation and type hints.
Enforces strict data consistency and validation rules.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, validator, ConfigDict
import numpy as np

class NodeType(str, Enum):
    """Types of nodes in the knowledge graph"""
    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    PERSON = "person"
    LOCATION = "location"
    ORGANIZATION = "organization"
    DOCUMENT = "document"
    CATEGORY = "category"

class RelationshipType(str, Enum):
    """Types of relationships between nodes"""
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    USES = "uses"
    CREATED_BY = "created_by"
    LOCATED_IN = "located_in"
    WORKS_FOR = "works_for"
    MENTIONS