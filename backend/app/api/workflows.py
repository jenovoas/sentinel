"""
Workflow Recommendation API
FastAPI endpoint for recommending workflows based on incident context
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from pathlib import Path
import re

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

# Load workflow index
WORKFLOW_INDEX_PATH = Path("/home/jnovoas/sentinel/workflow_index.json")
workflow_index = None


def load_workflow_index():
    """Load workflow index from JSON file"""
    global workflow_index
    if workflow_index is None:
        try:
            with open(WORKFLOW_INDEX_PATH, 'r', encoding='utf-8') as f:
                workflow_index = json.load(f)
        except Exception as e:
            print(f"Error loading workflow index: {e}")
            workflow_index = {"workflows": [], "metadata": {}}
    return workflow_index


class WorkflowRecommendationRequest(BaseModel):
    """Request model for workflow recommendations"""
    incident_description: str
    incident_type: Optional[str] = None
    limit: int = 5


class WorkflowRecommendation(BaseModel):
    """Workflow recommendation response"""
    id: str
    name: str
    description: str
    repository: str
    match_score: float
    security_score: float
    ai_score: float
    complexity_score: float
    node_count: int
    integrations: List[str]
    categories: List[str]
    reason: str


class WorkflowRecommendationResponse(BaseModel):
    """Response model for workflow recommendations"""
    total_workflows_available: int
    recommendations: List[WorkflowRecommendation]
    query: str


def calculate_match_score(workflow: Dict, query: str, incident_type: Optional[str] = None) -> tuple[float, str]:
    """
    Calculate how well a workflow matches the query
    Returns (score, reason)
    """
    query_lower = query.lower()
    score = 0.0
    reasons = []
    
    # Extract keywords from query
    keywords = set(re.findall(r'\b\w+\b', query_lower))
    
    # Check name match
    name_lower = workflow['name'].lower()
    name_matches = sum(1 for keyword in keywords if keyword in name_lower)
    if name_matches > 0:
        score += name_matches * 0.3
        reasons.append(f"Name matches ({name_matches} keywords)")
    
    # Check description match
    desc_lower = workflow['description'].lower()
    desc_matches = sum(1 for keyword in keywords if keyword in desc_lower)
    if desc_matches > 0:
        score += desc_matches * 0.2
        reasons.append(f"Description matches ({desc_matches} keywords)")
    
    # Boost security workflows for security incidents
    security_keywords = {'phishing', 'malware', 'threat', 'attack', 'breach', 'vulnerability', 
                        'suspicious', 'incident', 'alert', 'ioc', 'indicator'}
    if any(kw in query_lower for kw in security_keywords):
        if workflow['security_score'] > 0.3:
            score += workflow['security_score'] * 2.0
            reasons.append("Security-focused workflow")
    
    # Boost AI workflows for AI-related queries
    ai_keywords = {'ai', 'analyze', 'classification', 'detection', 'prediction', 'intelligence'}
    if any(kw in query_lower for kw in ai_keywords):
        if workflow['ai_score'] > 0.3:
            score += workflow['ai_score'] * 1.5
            reasons.append("AI-powered workflow")
    
    # Check integration matches
    integration_keywords = {'slack', 'jira', 'email', 'virustotal', 'shodan', 'api'}
    workflow_integrations = ' '.join(workflow['integrations']).lower()
    integration_matches = sum(1 for kw in integration_keywords if kw in workflow_integrations and kw in query_lower)
    if integration_matches > 0:
        score += integration_matches * 0.4
        reasons.append(f"Relevant integrations ({integration_matches})")
    
    # Incident type boost
    if incident_type:
        incident_type_lower = incident_type.lower()
        if incident_type_lower in name_lower or incident_type_lower in desc_lower:
            score += 1.0
            reasons.append(f"Matches incident type: {incident_type}")
    
    # Add base relevance score
    score += workflow['relevance_score'] * 0.5
    
    reason = " | ".join(reasons) if reasons else "General relevance"
    return score, reason


@router.post("/recommend", response_model=WorkflowRecommendationResponse)
async def recommend_workflows(request: WorkflowRecommendationRequest):
    """
    Recommend workflows based on incident description
    """
    index = load_workflow_index()
    
    if not index or not index.get('workflows'):
        raise HTTPException(status_code=500, detail="Workflow index not loaded")
    
    workflows = index['workflows']
    
    # Calculate match scores for all workflows
    scored_workflows = []
    for workflow in workflows:
        match_score, reason = calculate_match_score(
            workflow, 
            request.incident_description,
            request.incident_type
        )
        
        if match_score > 0:  # Only include workflows with some relevance
            scored_workflows.append({
                'workflow': workflow,
                'match_score': match_score,
                'reason': reason
            })
    
    # Sort by match score
    scored_workflows.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Take top N
    top_workflows = scored_workflows[:request.limit]
    
    # Format response
    recommendations = []
    for item in top_workflows:
        workflow = item['workflow']
        recommendations.append(WorkflowRecommendation(
            id=workflow['id'],
            name=workflow['name'],
            description=workflow['description'] or "No description available",
            repository=workflow['repository'],
            match_score=round(item['match_score'], 2),
            security_score=round(workflow['security_score'], 2),
            ai_score=round(workflow['ai_score'], 2),
            complexity_score=round(workflow['complexity_score'], 2),
            node_count=workflow['node_count'],
            integrations=workflow['integrations'][:5],  # Limit to top 5
            categories=workflow['categories'],
            reason=item['reason']
        ))
    
    return WorkflowRecommendationResponse(
        total_workflows_available=index['metadata']['total_workflows'],
        recommendations=recommendations,
        query=request.incident_description
    )


@router.get("/stats")
async def get_workflow_stats():
    """Get workflow statistics"""
    index = load_workflow_index()
    
    if not index:
        raise HTTPException(status_code=500, detail="Workflow index not loaded")
    
    return {
        "total_workflows": index['metadata']['total_workflows'],
        "repositories": index['metadata']['repositories'],
        "report": index.get('report', {}),
        "generated_at": index['metadata']['generated_at']
    }


@router.get("/categories")
async def get_categories():
    """Get available workflow categories"""
    index = load_workflow_index()
    
    if not index or 'report' not in index:
        raise HTTPException(status_code=500, detail="Workflow index not loaded")
    
    return {
        "categories": index['report'].get('category_distribution', {}),
        "total_workflows": index['metadata']['total_workflows']
    }
