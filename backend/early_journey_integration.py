"""
Early Mortgage Journey Integration Module for RBC Mortgage & Creditor Insurance Advisor Assistant
Provides tools to integrate protection discussions earlier in the mortgage journey
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field

from backend.mortgage_journey import (
    MortgageJourneyStage,
    MortgageType,
    ProtectionDiscussionStatus,
    LifeEvent,
    get_journey_stage_description
)

class ProtectionOpportunity(BaseModel):
    """Model for a protection discussion opportunity"""
    opportunity_id: str
    client_id: str
    journey_stage: MortgageJourneyStage
    opportunity_type: str  # "ideal_timing", "life_event", "risk_factor", etc.
    description: str
    talking_points: List[str]
    priority: str  # "high", "medium", "low"
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
class ProtectionDiscussionTracker(BaseModel):
    """Model to track protection discussions with a client"""
    client_id: str
    discussion_history: List[Dict[str, Any]] = []
    client_objections: List[str] = []
    client_interests: List[str] = []
    next_discussion_stage: Optional[MortgageJourneyStage] = None
    
    def add_discussion(self, 
                      stage: MortgageJourneyStage, 
                      status: ProtectionDiscussionStatus,
                      notes: str = "",
                      objections: List[str] = None,
                      interests: List[str] = None):
        """Record a protection discussion with the client"""
        discussion = {
            "date": datetime.now(),
            "stage": stage,
            "status": status,
            "notes": notes
        }
        self.discussion_history.append(discussion)
        
        if objections:
            for objection in objections:
                if objection not in self.client_objections:
                    self.client_objections.append(objection)
        
        if interests:
            for interest in interests:
                if interest not in self.client_interests:
                    self.client_interests.append(interest)
        
        # Determine next best stage for discussion based on current status
        if status in [ProtectionDiscussionStatus.NOT_DISCUSSED, ProtectionDiscussionStatus.BRIEFLY_MENTIONED]:
            # If not discussed or only briefly mentioned, suggest next stage for detailed discussion
            current_stage_index = list(MortgageJourneyStage).index(stage)
            if current_stage_index < len(list(MortgageJourneyStage)) - 1:
                self.next_discussion_stage = list(MortgageJourneyStage)[current_stage_index + 1]
            else:
                self.next_discussion_stage = stage
        elif status == ProtectionDiscussionStatus.DETAILED_DISCUSSION:
            # If detailed discussion happened, next stage should be for follow-up
            self.next_discussion_stage = stage  # Suggest following up in same stage
        else:
            # If client showed interest or selected protection, no need for next discussion
            self.next_discussion_stage = None

def identify_protection_opportunities(
    client_data: Dict[str, Any],
    journey_stage: MortgageJourneyStage,
    mortgage_type: MortgageType,
    life_events: List[LifeEvent] = None,
    previous_discussions: Optional[ProtectionDiscussionTracker] = None
) -> List[ProtectionOpportunity]:
    """
    Identify opportunities to discuss protection based on client data,
    mortgage journey stage, and any recent life events
    """
    opportunities = []
    
    # Get stage information
    stage_info = get_journey_stage_description(journey_stage)
    
    # Check if current stage is ideal for protection discussion
    ideal_stages = {
        MortgageType.NEW_PURCHASE: MortgageJourneyStage.DOCUMENTATION_COLLECTION,
        MortgageType.REFINANCE: MortgageJourneyStage.DOCUMENTATION_COLLECTION,
        MortgageType.RENEWAL: MortgageJourneyStage.INITIAL_INQUIRY,
        MortgageType.TRANSFER: MortgageJourneyStage.DOCUMENTATION_COLLECTION,
        MortgageType.INVESTMENT_PROPERTY: MortgageJourneyStage.APPLICATION_SUBMISSION
    }
    
    if journey_stage == ideal_stages.get(mortgage_type, MortgageJourneyStage.DOCUMENTATION_COLLECTION):
        opportunities.append(
            ProtectionOpportunity(
                opportunity_id=f"ideal_timing_{client_data.get('client_id', 'unknown')}",
                client_id=client_data.get("client_id", "unknown"),
                journey_stage=journey_stage,
                opportunity_type="ideal_timing",
                description=f"Ideal stage to discuss protection for {mortgage_type.value} mortgage",
                talking_points=stage_info.get("protection_talking_points", []),
                priority="high"
            )
        )
    
    # Check for life event triggers
    if life_events:
        for event in life_events:
            from backend.conversation_guides import get_life_event_protection_talking_points
            talking_points = get_life_event_protection_talking_points(event)
            
            opportunities.append(
                ProtectionOpportunity(
                    opportunity_id=f"life_event_{event.value}_{client_data.get('client_id', 'unknown')}",
                    client_id=client_data.get("client_id", "unknown"),
                    journey_stage=journey_stage,
                    opportunity_type="life_event",
                    description=f"Protection opportunity based on life event: {event.value}",
                    talking_points=talking_points,
                    priority="high"
                )
            )
    
    # Check for risk factors in client profile
    risk_factors = []
    
    if client_data.get("dependents", 0) > 0:
        risk_factors.append("dependents")
        opportunities.append(
            ProtectionOpportunity(
                opportunity_id=f"risk_dependents_{client_data.get('client_id', 'unknown')}",
                client_id=client_data.get("client_id", "unknown"),
                journey_stage=journey_stage,
                opportunity_type="risk_factor",
                description="Client has dependents who rely on their income",
                talking_points=[
                    f"With {client_data.get('dependents')} dependents, protecting your mortgage is an important part of ensuring their financial security.",
                    "HomeProtector insurance ensures your family can stay in their home even if something happens to you."
                ],
                priority="high"
            )
        )
    
    if client_data.get("mortgage_amount", 0) > client_data.get("annual_income", 0) * 3:
        risk_factors.append("high_mortgage_to_income")
        opportunities.append(
            ProtectionOpportunity(
                opportunity_id=f"risk_mortgage_income_{client_data.get('client_id', 'unknown')}",
                client_id=client_data.get("client_id", "unknown"),
                journey_stage=journey_stage,
                opportunity_type="risk_factor",
                description="Client has high mortgage-to-income ratio",
                talking_points=[
                    "Your mortgage payments represent a significant portion of your income, which could make it challenging to maintain if your income was interrupted.",
                    "Disability and job loss protection can help ensure you can keep making payments even if you're unable to work temporarily."
                ],
                priority="medium"
            )
        )
    
    if client_data.get("years_at_current_job", 0) < 2:
        risk_factors.append("job_stability")
        opportunities.append(
            ProtectionOpportunity(
                opportunity_id=f"risk_job_stability_{client_data.get('client_id', 'unknown')}",
                client_id=client_data.get("client_id", "unknown"),
                journey_stage=journey_stage,
                opportunity_type="risk_factor",
                description="Client has limited job tenure",
                talking_points=[
                    "With less than two years at your current job, you might not qualify for full benefits or severance if something unexpected happened.",
                    "Job loss protection can provide a safety net while you're establishing yourself in your role."
                ],
                priority="medium"
            )
        )
    
    # Check if this is last opportunity before funding
    if journey_stage in [MortgageJourneyStage.APPROVAL, MortgageJourneyStage.CLOSING]:
        opportunities.append(
            ProtectionOpportunity(
                opportunity_id=f"last_opportunity_{client_data.get('client_id', 'unknown')}",
                client_id=client_data.get("client_id", "unknown"),
                journey_stage=journey_stage,
                opportunity_type="last_opportunity",
                description="Last opportunity to easily add protection before funding",
                talking_points=[
                    "This is the last opportunity to easily add protection coverage before your mortgage is funded.",
                    "After funding, adding protection would require a separate application process."
                ],
                priority="high"
            )
        )
    
    # If there have been previous discussions, check if follow-up is needed
    if previous_discussions and previous_discussions.next_discussion_stage == journey_stage:
        opportunities.append(
            ProtectionOpportunity(
                opportunity_id=f"follow_up_{client_data.get('client_id', 'unknown')}",
                client_id=client_data.get("client_id", "unknown"),
                journey_stage=journey_stage,
                opportunity_type="follow_up",
                description="Follow up on previous protection discussion",
                talking_points=[
                    "I wanted to follow up on our previous conversation about mortgage protection.",
                    "Have you had a chance to think about the protection options we discussed?",
                    "Do you have any questions I can answer about how the coverage works?"
                ],
                priority="medium"
            )
        )
    
    return opportunities

def generate_protection_discussion_guide(
    client_data: Dict[str, Any],
    journey_stage: MortgageJourneyStage,
    mortgage_type: MortgageType,
    life_events: List[LifeEvent] = None,
    previous_discussions: Optional[ProtectionDiscussionTracker] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive guide for discussing protection with a client
    at their current mortgage journey stage
    """
    # Identify opportunities
    opportunities = identify_protection_opportunities(
        client_data, journey_stage, mortgage_type, life_events, previous_discussions
    )
    
    # Get stage information
    stage_info = get_journey_stage_description(journey_stage)
    
    # Determine if this is the optimal time to discuss protection
    is_optimal_time = journey_stage == MortgageJourneyStage.DOCUMENTATION_COLLECTION
    
    # Determine priority level for discussion
    priority = "low"
    if is_optimal_time:
        priority = "high"
    elif journey_stage in [MortgageJourneyStage.APPROVAL, MortgageJourneyStage.CLOSING]:
        priority = "high"  # Last chance before funding
    elif any(opp.priority == "high" for opp in opportunities):
        priority = "high"
    elif any(opp.priority == "medium" for opp in opportunities):
        priority = "medium"
    
    # Compile talking points from all opportunities
    all_talking_points = []
    for opp in opportunities:
        all_talking_points.extend(opp.talking_points)
    
    # Remove duplicates while preserving order
    unique_talking_points = []
    for point in all_talking_points:
        if point not in unique_talking_points:
            unique_talking_points.append(point)
    
    # Generate introduction based on stage and opportunities
    introduction = f"This is a good time to discuss mortgage protection because you're at the {stage_info.get('name', journey_stage.value)} stage of your mortgage journey."
    
    if any(opp.opportunity_type == "life_event" for opp in opportunities):
        introduction += " Recent changes in your life situation make protection particularly relevant now."
    
    if any(opp.opportunity_type == "last_opportunity" for opp in opportunities):
        introduction += " This is one of the last opportunities to easily add protection before your mortgage is funded."
    
    # Generate objection handling guidance
    from backend.conversation_guides import get_objection_handling_tips
    objection_tips = get_objection_handling_tips()
    
    # If there are previous objections, prioritize those tips
    prioritized_objection_tips = {}
    if previous_discussions and previous_discussions.client_objections:
        for objection in previous_discussions.client_objections:
            for key, tips in objection_tips.items():
                if key in objection.lower():
                    prioritized_objection_tips[objection] = tips
    
    # Add other general tips
    for key, tips in objection_tips.items():
        if key not in prioritized_objection_tips:
            prioritized_objection_tips[key] = tips
    
    # Compile the complete guide
    guide = {
        "client_name": client_data.get("full_name", "Client"),
        "journey_stage": stage_info.get("name", journey_stage.value),
        "mortgage_type": mortgage_type.value,
        "is_optimal_time": is_optimal_time,
        "priority": priority,
        "introduction": introduction,
        "client_concerns": stage_info.get("client_concerns", []),
        "talking_points": unique_talking_points,
        "objection_handling": prioritized_objection_tips,
        "opportunities": [opp.dict() for opp in opportunities],
        "recommended_next_steps": []
    }
    
    # Add recommended next steps based on stage and previous discussions
    if journey_stage in [MortgageJourneyStage.INITIAL_INQUIRY, MortgageJourneyStage.RATE_SHOPPING]:
        guide["recommended_next_steps"] = [
            "Briefly introduce protection concept",
            "Note any initial reactions for future discussions",
            "Plan for detailed discussion during documentation collection"
        ]
    elif journey_stage == MortgageJourneyStage.DOCUMENTATION_COLLECTION:
        guide["recommended_next_steps"] = [
            "Have detailed protection discussion",
            "Show specific coverage amounts and premiums",
            "Address any objections",
            "Get initial indication of interest"
        ]
    elif journey_stage in [MortgageJourneyStage.APPLICATION_SUBMISSION, MortgageJourneyStage.APPROVAL]:
        guide["recommended_next_steps"] = [
            "Follow up on previous protection discussion",
            "Address any remaining questions or concerns",
            "Begin protection application if client is interested"
        ]
    elif journey_stage in [MortgageJourneyStage.CLOSING, MortgageJourneyStage.FUNDING]:
        guide["recommended_next_steps"] = [
            "Last opportunity to add protection easily",
            "Finalize protection choices",
            "Complete protection application"
        ]
    
    return guide
