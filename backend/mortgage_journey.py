"""
Mortgage Journey Module for RBC Mortgage & Creditor Insurance Advisor Assistant
Defines the stages of the mortgage journey and provides tools for tracking client progress
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

class MortgageJourneyStage(str, Enum):
    """Stages in the mortgage journey"""
    INITIAL_INQUIRY = "initial_inquiry"
    RATE_SHOPPING = "rate_shopping"
    DOCUMENTATION_COLLECTION = "documentation_collection"
    APPLICATION_SUBMISSION = "application_submission"
    APPROVAL = "approval"
    CLOSING = "closing"
    FUNDING = "funding"
    POST_FUNDING = "post_funding"

class MortgageType(str, Enum):
    """Types of mortgages"""
    NEW_PURCHASE = "new_purchase"
    REFINANCE = "refinance"
    RENEWAL = "renewal"
    TRANSFER = "transfer"
    INVESTMENT_PROPERTY = "investment_property"

class ProtectionDiscussionStatus(str, Enum):
    """Status of creditor protection discussion"""
    NOT_DISCUSSED = "not_discussed"
    BRIEFLY_MENTIONED = "briefly_mentioned"
    DETAILED_DISCUSSION = "detailed_discussion"
    CLIENT_INTERESTED = "client_interested"
    CLIENT_DECLINED = "client_declined"
    PROTECTION_SELECTED = "protection_selected"

class LifeEvent(str, Enum):
    """Life events that might trigger insurance needs"""
    NEW_HOME_PURCHASE = "new_home_purchase"
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    NEW_CHILD = "new_child"
    CAREER_CHANGE = "career_change"
    RETIREMENT_PLANNING = "retirement_planning"
    HEALTH_CHANGE = "health_change"
    INCOME_CHANGE = "income_change"
    DEPENDENT_CARE = "dependent_care"

class MortgageJourney(BaseModel):
    """Model to track a client's mortgage journey"""
    client_id: str
    mortgage_type: MortgageType
    current_stage: MortgageJourneyStage = MortgageJourneyStage.INITIAL_INQUIRY
    started_at: datetime = Field(default_factory=datetime.now)
    estimated_closing_date: Optional[datetime] = None
    protection_discussion: ProtectionDiscussionStatus = ProtectionDiscussionStatus.NOT_DISCUSSED
    protection_discussion_date: Optional[datetime] = None
    recent_life_events: List[LifeEvent] = []
    stage_history: Dict[str, datetime] = Field(default_factory=dict)
    notes: Dict[str, str] = Field(default_factory=dict)
    
    def update_stage(self, new_stage: MortgageJourneyStage, notes: Optional[str] = None):
        """Update the current stage of the mortgage journey"""
        self.current_stage = new_stage
        self.stage_history[new_stage] = datetime.now()
        if notes:
            self.notes[new_stage] = notes
    
    def update_protection_discussion(self, status: ProtectionDiscussionStatus, notes: Optional[str] = None):
        """Update the status of the creditor protection discussion"""
        self.protection_discussion = status
        self.protection_discussion_date = datetime.now()
        if notes:
            self.notes[f"protection_{status}"] = notes
    
    def add_life_event(self, event: LifeEvent, notes: Optional[str] = None):
        """Add a life event to the client's profile"""
        if event not in self.recent_life_events:
            self.recent_life_events.append(event)
        if notes:
            self.notes[f"life_event_{event}"] = notes
    
    def get_stage_duration(self, stage: MortgageJourneyStage) -> Optional[timedelta]:
        """Get the duration spent in a particular stage"""
        if stage not in self.stage_history:
            return None
            
        stage_start = self.stage_history[stage]
        
        # Find the next stage after this one
        stages_order = list(MortgageJourneyStage)
        stage_index = stages_order.index(stage)
        
        if stage_index + 1 < len(stages_order):
            next_stage = stages_order[stage_index + 1]
            if next_stage in self.stage_history:
                return self.stage_history[next_stage] - stage_start
        
        # If this is the current stage or there's no next stage recorded
        return datetime.now() - stage_start
    
    def get_optimal_protection_discussion_stage(self) -> MortgageJourneyStage:
        """
        Determine the optimal stage to discuss creditor protection
        based on mortgage type and client profile
        """
        # For most mortgage types, documentation collection is the ideal time
        if self.mortgage_type in [MortgageType.NEW_PURCHASE, MortgageType.TRANSFER]:
            return MortgageJourneyStage.DOCUMENTATION_COLLECTION
        
        # For renewals, initial inquiry is a good time
        if self.mortgage_type == MortgageType.RENEWAL:
            return MortgageJourneyStage.INITIAL_INQUIRY
        
        # Default recommendation
        return MortgageJourneyStage.DOCUMENTATION_COLLECTION
    
    def should_discuss_protection_now(self) -> bool:
        """
        Determine if protection should be discussed at the current stage
        """
        optimal_stage = self.get_optimal_protection_discussion_stage()
        
        # If we're at or past the optimal stage and haven't had a detailed discussion
        if (list(MortgageJourneyStage).index(self.current_stage) >= 
            list(MortgageJourneyStage).index(optimal_stage) and
            self.protection_discussion in [
                ProtectionDiscussionStatus.NOT_DISCUSSED,
                ProtectionDiscussionStatus.BRIEFLY_MENTIONED
            ]):
            return True
            
        # If there are life events that suggest protection needs
        if len(self.recent_life_events) > 0 and self.protection_discussion != ProtectionDiscussionStatus.PROTECTION_SELECTED:
            return True
            
        return False

def get_journey_stage_description(stage: MortgageJourneyStage) -> Dict[str, Any]:
    """
    Get detailed information about a mortgage journey stage
    including recommended actions and talking points
    """
    stage_info = {
        MortgageJourneyStage.INITIAL_INQUIRY: {
            "name": "Initial Inquiry",
            "description": "Client's first contact expressing interest in a mortgage product",
            "typical_duration": "1-3 days",
            "client_concerns": [
                "Getting the best rate",
                "Understanding how much they can afford",
                "Learning about the mortgage process"
            ],
            "advisor_actions": [
                "Collect basic client information",
                "Discuss rate options",
                "Explain the mortgage process",
                "Briefly introduce the concept of mortgage protection"
            ],
            "protection_talking_points": [
                "As we begin your mortgage journey, I'd like to mention that RBC offers protection options that can safeguard your mortgage in case of unexpected events.",
                "We'll discuss this in more detail as we move forward, but it's something to keep in mind as you consider your overall financial picture."
            ]
        },
        MortgageJourneyStage.RATE_SHOPPING: {
            "name": "Rate Shopping",
            "description": "Client is comparing rates from different lenders",
            "typical_duration": "3-7 days",
            "client_concerns": [
                "Finding the lowest interest rate",
                "Understanding different mortgage products",
                "Comparing offers from different lenders"
            ],
            "advisor_actions": [
                "Present competitive rate options",
                "Explain the benefits of different mortgage terms",
                "Highlight RBC's overall value proposition",
                "Begin to assess client's risk profile"
            ],
            "protection_talking_points": [
                "While rate is important, it's also worth considering the overall protection of your investment.",
                "RBC's mortgage protection can be a valuable complement to your mortgage, providing peace of mind at a reasonable cost."
            ]
        },
        MortgageJourneyStage.DOCUMENTATION_COLLECTION: {
            "name": "Documentation Collection",
            "description": "Gathering necessary financial documents for the application",
            "typical_duration": "7-14 days",
            "client_concerns": [
                "Understanding what documents are needed",
                "Ensuring their financial situation looks favorable",
                "Moving the process forward efficiently"
            ],
            "advisor_actions": [
                "Request and organize client documents",
                "Assess client's financial situation",
                "Identify potential risks or gaps in protection",
                "Have a detailed discussion about creditor insurance options"
            ],
            "protection_talking_points": [
                "As I review your financial documents, I notice some potential areas where protection could be valuable for you.",
                "Let's take a few minutes to discuss how mortgage protection works and how it might fit into your overall financial plan.",
                "Based on your situation with [specific details like dependents, single income, etc.], here's how our protection options could help..."
            ]
        },
        MortgageJourneyStage.APPLICATION_SUBMISSION: {
            "name": "Application Submission",
            "description": "Formal mortgage application is submitted for approval",
            "typical_duration": "1-3 days",
            "client_concerns": [
                "Getting approved for the desired amount",
                "Understanding next steps",
                "Timeline for approval"
            ],
            "advisor_actions": [
                "Submit complete application package",
                "Set expectations for approval timeline",
                "Follow up on protection discussion if not yet completed"
            ],
            "protection_talking_points": [
                "Now that we've submitted your application, let's make sure we've considered all aspects of your mortgage plan.",
                "Have you had a chance to think about the protection options we discussed? I'm happy to answer any questions."
            ]
        },
        MortgageJourneyStage.APPROVAL: {
            "name": "Approval",
            "description": "Mortgage application has been approved",
            "typical_duration": "1-3 days",
            "client_concerns": [
                "Understanding the terms of approval",
                "Next steps to finalize the mortgage",
                "Preparing for closing"
            ],
            "advisor_actions": [
                "Explain approval details",
                "Discuss next steps",
                "Finalize protection options if client is interested"
            ],
            "protection_talking_points": [
                "Congratulations on your mortgage approval! Now is a good time to finalize your protection plan.",
                "Adding protection now is simple and can be processed alongside your mortgage documents."
            ]
        },
        MortgageJourneyStage.CLOSING: {
            "name": "Closing",
            "description": "Final paperwork and signing",
            "typical_duration": "1-7 days",
            "client_concerns": [
                "Understanding all documents they're signing",
                "Ensuring everything is in order",
                "Finalizing all aspects of the mortgage"
            ],
            "advisor_actions": [
                "Review all documents with client",
                "Ensure all questions are answered",
                "Last opportunity to add protection"
            ],
            "protection_talking_points": [
                "As we finalize your mortgage, I want to ensure you've made an informed decision about protection.",
                "This is the last opportunity to easily add protection coverage before your mortgage is funded."
            ]
        },
        MortgageJourneyStage.FUNDING: {
            "name": "Funding",
            "description": "Funds are disbursed",
            "typical_duration": "1-3 days",
            "client_concerns": [
                "Ensuring funds are transferred correctly",
                "Understanding when they can take possession",
                "Confirming all conditions have been met"
            ],
            "advisor_actions": [
                "Coordinate with all parties for funding",
                "Confirm protection choices are processed if selected"
            ],
            "protection_talking_points": [
                "Your mortgage is now being funded. If you've chosen protection, that will be processed simultaneously.",
                "If you haven't added protection, we can still discuss options after funding, though it will require a separate application."
            ]
        },
        MortgageJourneyStage.POST_FUNDING: {
            "name": "Post-Funding",
            "description": "Mortgage is active and client has taken possession",
            "typical_duration": "Ongoing",
            "client_concerns": [
                "Understanding payment procedures",
                "Knowing who to contact with questions",
                "Managing their new financial responsibility"
            ],
            "advisor_actions": [
                "Check in with client after move-in",
                "Ensure they understand payment procedures",
                "Discuss protection options if not yet added"
            ],
            "protection_talking_points": [
                "Now that you're settled in your new home, it's a good time to revisit protection options if you haven't already.",
                "Many clients find that the reality of mortgage payments brings new perspective on the value of protection."
            ]
        }
    }
    
    return stage_info.get(stage, {})

def get_life_event_protection_talking_points(event: LifeEvent) -> List[str]:
    """
    Get talking points about protection that are relevant to specific life events
    """
    talking_points = {
        LifeEvent.NEW_HOME_PURCHASE: [
            "A new home is one of the biggest investments you'll make. Protection ensures this investment remains secure even if unexpected events occur.",
            "HomeProtector insurance can help ensure your family keeps their home even if you're unable to make payments due to disability, critical illness, or death."
        ],
        LifeEvent.MARRIAGE: [
            "Congratulations on your marriage! As you combine your lives, it's important to think about how you'll protect each other financially.",
            "Joint mortgage protection can be more cost-effective than individual policies and ensures either spouse can keep the home if something happens to the other."
        ],
        LifeEvent.DIVORCE: [
            "During this transition, it's important to reassess your protection needs, especially if responsibility for the mortgage is changing.",
            "Individual protection can provide peace of mind as you navigate this new chapter independently."
        ],
        LifeEvent.NEW_CHILD: [
            "Congratulations on your growing family! With a new child, ensuring your family can stay in their home becomes even more important.",
            "Mortgage protection provides security knowing your child will have a stable home environment regardless of what happens."
        ],
        LifeEvent.CAREER_CHANGE: [
            "A career change often means changes in benefits, including any workplace disability or life insurance.",
            "Mortgage protection can fill gaps in your new benefits package and provide consistent coverage regardless of where you work."
        ],
        LifeEvent.RETIREMENT_PLANNING: [
            "As you plan for retirement, it's important to consider how your mortgage fits into your overall plan.",
            "Protection can be especially valuable during this transition to ensure unexpected health events don't derail your retirement plans."
        ],
        LifeEvent.HEALTH_CHANGE: [
            "Changes in health can affect future insurability. Securing protection now ensures you have coverage regardless of future health developments.",
            "Our critical illness protection can help cover mortgage payments if you're diagnosed with a covered condition."
        ],
        LifeEvent.INCOME_CHANGE: [
            "With changes in your income, it's important to reassess how you would manage your mortgage payments in case of disability or illness.",
            "Our disability protection can replace a portion of your income specifically for your mortgage payments if you're unable to work."
        ],
        LifeEvent.DEPENDENT_CARE: [
            "Taking on responsibility for caring for a dependent adds financial obligations that make protection even more important.",
            "Mortgage protection ensures your dependent would have a secure place to live even if something happened to you."
        ]
    }
    
    return talking_points.get(event, [
        "Life changes often bring new financial responsibilities and protection needs.",
        "Let's discuss how your recent life changes might affect your need for mortgage protection."
    ])
