import re
from typing import List, Dict, Any, Tuple, Optional

# Constants for Priority Keywords
HIGH_PRIORITY_KEYWORDS = {"outage", "security", "production", "critical", "data loss", "down", "offline", "broken database", "breach"}
MEDIUM_PRIORITY_KEYWORDS = {"application errors", "performance issues", "error", "slow", "bug", "failed", "fail", "warning", "latency"}
LOW_PRIORITY_KEYWORDS = {"request", "documentation", "general question", "how to", "setup", "question", "license", "chair"}

STOP_WORDS = {"the", "is", "a", "to", "in", "on", "for", "and", "of", "my", "i", "unable", "cannot", "not", "have", "with", "this", "it", "me"}

def tokenize(text: str) -> set:
    """Helper to convert text into a clean set of alphanumeric lowercase word tokens, excluding stop words."""
    if not text:
        return set()
    # Replace non-alphanumeric chars with spaces and convert to lowercase
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    words = clean_text.split()
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}

def calculate_jaccard_similarity(set1: set, set2: set) -> float:
    """Calculate the Jaccard similarity coefficient between two sets of tokens."""
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def classify_priority(issue_text: str) -> str:
    """
    Classify the priority of a support issue based on text keywords.
    Returns: LOW, MEDIUM, HIGH, or CRITICAL.
    """
    text_lower = issue_text.lower()
    
    # 1. High Priority detection
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            # If it's a production outage, elevate it to CRITICAL for better Helpdesk SLA
            if "outage" in text_lower or "production" in text_lower:
                return "CRITICAL"
            return "HIGH"
            
    # 2. Medium Priority detection
    for keyword in MEDIUM_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            return "MEDIUM"
            
    # Default is LOW
    return "LOW"

def generate_plan(issue_text: str) -> List[str]:
    """Generates an execution plan outlining the steps the agent will perform."""
    priority = classify_priority(issue_text)
    return [
        f"1. Classify priority of user request (Detected: {priority}).",
        "2. Query Helpdesk Knowledge Base (search_kb) to find relevant troubleshooting guides.",
        "3. List all support tickets in the system (list_tickets).",
        "4. Run similarity assessment between user request and active tickets.",
        "5. Branching Decision Logic: If active duplicate exists, add_comment(). Else, create_ticket().",
        "6. Construct final summary response linking ticket references and KB guidance."
    ]

def is_duplicate_ticket(
    issue_title: str, 
    issue_desc: str, 
    existing_tickets: List[Dict[str, Any]], 
    threshold: float = 0.25
) -> Tuple[bool, Optional[int], float]:
    """
    Scans existing open tickets to detect duplicate issues.
    Uses title overlap, description word-level Jaccard similarity, and keyword matching.
    
    Returns:
        Tuple[is_duplicate, ticket_id, similarity_score]
    """
    user_title_tokens = tokenize(issue_title)
    user_desc_tokens = tokenize(issue_desc)
    combined_user_tokens = user_title_tokens.union(user_desc_tokens)
    
    best_score = 0.0
    matching_ticket_id = None
    
    for t in existing_tickets:
        # We only consider tickets in progress or open for duplicate matching.
        # Resolved/Closed tickets are not duplicates (a new issue should be opened or re-evaluated).
        status = t.get("status", "").upper()
        if status not in ["OPEN", "IN_PROGRESS"]:
            continue
            
        t_title = t.get("title", "")
        t_desc = t.get("description", "")
        
        t_title_tokens = tokenize(t_title)
        t_desc_tokens = tokenize(t_desc)
        combined_ticket_tokens = t_title_tokens.union(t_desc_tokens)
        
        # Calculate individual metrics
        title_similarity = calculate_jaccard_similarity(user_title_tokens, t_title_tokens)
        desc_similarity = calculate_jaccard_similarity(user_desc_tokens, t_desc_tokens)
        overall_similarity = calculate_jaccard_similarity(combined_user_tokens, combined_ticket_tokens)
        
        # Weighted score: title similarity carries more weight (60%) than description (40%)
        weighted_score = (title_similarity * 0.6) + (desc_similarity * 0.4)
        
        # Take the maximum of weighted and overall jaccard score
        final_score = max(weighted_score, overall_similarity)
        
        # Also do a quick direct check: if the title is a substring of the other title
        if (len(t_title) > 3 and len(issue_title) > 3) and (t_title.lower() in issue_title.lower() or issue_title.lower() in t_title.lower()):
            final_score = max(final_score, 0.6)
            
        if final_score > best_score:
            best_score = final_score
            matching_ticket_id = t.get("id")
            
    # Determine if duplicate based on threshold
    is_dup = best_score >= threshold
    return is_dup, matching_ticket_id, round(best_score, 2)
