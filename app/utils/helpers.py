from datetime import datetime
from flask import current_app
import math

def calculate_feasibility(job):
    """
    Calculate the feasibility score (0-100) for a job based on multiple factors
    
    Args:
        job (dict): Job details including budget, duration, skills, etc.
        
    Returns:
        float: Feasibility score between 0-100
    """
    try:
        # Default weights for different factors
        weights = {
            'budget': 0.4,
            'duration': 0.3,
            'skill_match': 0.2,
            'client_rating': 0.1
        }
        
        # Normalize budget score (0-1)
        budget = float(job.get('budget', 0))
        budget_score = min(budget / 1000, 1.0)  # Cap at $1000
        
        # Normalize duration score (shorter = better)
        duration_days = int(job.get('duration_days', 30))
        duration_score = 1 - min(duration_days / 30, 1.0)
        
        # Skill match (simple binary for now)
        required_skills = job.get('skills', [])
        available_skills = current_app.config.get('TEAM_SKILLS', [])
        skill_score = 1.0 if any(skill in available_skills for skill in required_skills) else 0.5
        
        # Client rating (if available)
        client_rating = float(job.get('client_rating', 0))
        rating_score = client_rating / 5.0  # Normalize to 0-1
        
        # Calculate weighted score
        feasibility = (
            weights['budget'] * budget_score +
            weights['duration'] * duration_score +
            weights['skill_match'] * skill_score +
            weights['client_rating'] * rating_score
        ) * 100  # Convert to percentage
        
        return round(feasibility, 2)
        
    except Exception as e:
        current_app.logger.error(f"Error calculating feasibility: {str(e)}")
        return 0.0

def calculate_workload(member_id):
    """
    Calculate current workload for a team member (0-100%)
    
    Args:
        member_id (int): User ID of the team member
        
    Returns:
        float: Workload percentage
    """
    try:
        from app.models import Task
        
        # Count active tasks
        active_tasks = Task.query.filter_by(
            assignee_id=member_id,
            status='in_progress'
        ).count()
        
        # Simple heuristic: each active task = 20% workload
        workload = min(100, active_tasks * 20)
        
        return workload
        
    except Exception as e:
        current_app.logger.error(f"Error calculating workload: {str(e)}")
        return 0.0

def format_deadline(deadline):
    """
    Format deadline datetime for display
    
    Args:
        deadline (datetime): Deadline datetime
        
    Returns:
        str: Formatted string
    """
    if not deadline:
        return "No deadline"
    
    now = datetime.utcnow()
    delta = deadline - now
    
    if delta.days < 0:
        return f"Overdue by {-delta.days} days"
    elif delta.days == 0:
        return "Due today"
    elif delta.days == 1:
        return "Due tomorrow"
    elif delta.days < 7:
        return f"Due in {delta.days} days"
    else:
        return deadline.strftime("%b %d, %Y")

def calculate_expected_profit(budget, hours_required):
    """
    Calculate expected profit based on budget and estimated hours
    
    Args:
        budget (float): Project budget
        hours_required (float): Estimated hours needed
        
    Returns:
        dict: Dictionary with cost, profit, and margin
    """
    try:
        hourly_rate = current_app.config.get('HOURLY_RATE', 25)
        cost = hours_required * hourly_rate
        profit = budget - cost
        margin = (profit / budget) * 100 if budget > 0 else 0
        
        return {
            'cost': round(cost, 2),
            'profit': round(profit, 2),
            'margin': round(margin, 2)
        }
        
    except Exception as e:
        current_app.logger.error(f"Error calculating profit: {str(e)}")
        return {
            'cost': 0,
            'profit': 0,
            'margin': 0
        }