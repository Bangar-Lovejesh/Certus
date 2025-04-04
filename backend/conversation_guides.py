"""
Conversation Guides Module for RBC Mortgage & Creditor Insurance Advisor Assistant
Provides structured conversation templates and personalized talking points
for different stages of the mortgage journey
"""
from typing import List, Dict, Any, Optional
import random
from pydantic import BaseModel

from backend.mortgage_journey import (
    MortgageJourneyStage,
    LifeEvent,
    get_journey_stage_description,
    get_life_event_protection_talking_points
)

class ConversationTemplate(BaseModel):
    """Model for a conversation template"""
    title: str
    description: str
    objective: str
    key_questions: List[str]
    talking_points: List[str]
    objection_responses: Dict[str, str]
    
class PersonalizedGuide(BaseModel):
    """Model for a personalized conversation guide"""
    template: ConversationTemplate
    client_specific_points: List[str]
    recommended_timing: str
    next_steps: List[str]

def get_discovery_conversation_template() -> ConversationTemplate:
    """Get template for initial discovery conversation"""
    return ConversationTemplate(
        title="Client Needs Discovery",
        description="Initial conversation to understand client's mortgage needs and life situation",
        objective="Uncover client's needs, concerns, and life events that might impact their mortgage and protection needs",
        key_questions=[
            "What's prompting you to look for a mortgage at this time?",
            "Have there been any recent changes in your life situation? (marriage, children, job change, etc.)",
            "What are your biggest concerns about taking on a mortgage?",
            "How would you handle your mortgage payments if you were unable to work due to illness or injury?",
            "What existing protection do you have in place? (life insurance, disability coverage, critical illness, etc.)",
            "How long do you plan to stay in this home?"
        ],
        talking_points=[
            "Understanding your overall situation helps me recommend the right mortgage and protection options for you.",
            "Many clients don't realize how a disability or critical illness could impact their ability to make mortgage payments.",
            "Mortgage protection is often more affordable than people expect, especially when set up at the same time as your mortgage."
        ],
        objection_responses={
            "I already have life insurance": "That's great! Existing coverage is important to consider. Mortgage protection can complement your current insurance by being specifically dedicated to your mortgage, leaving other insurance for your family's ongoing expenses.",
            
            "It's too expensive": "I understand cost is a concern. Let's look at the actual numbers for your situation. Many clients find that protection costs less than they expected, especially when compared to the potential financial impact of being unprotected.",
            
            "I'll think about it later": "I understand wanting to focus on the mortgage first. However, this is actually the ideal time to consider protection because it's easier to set up alongside your mortgage, and you'll be immediately protected once your mortgage funds."
        }
    )

def get_protection_benefits_template() -> ConversationTemplate:
    """Get template for explaining protection benefits"""
    return ConversationTemplate(
        title="Mortgage Protection Benefits",
        description="Detailed explanation of how mortgage protection works and its benefits",
        objective="Help client understand the specific benefits and mechanics of mortgage protection",
        key_questions=[
            "What aspects of mortgage protection are most important to you?",
            "Between life, disability, critical illness, and job loss coverage, which concerns you most?",
            "How would your family manage the mortgage if something happened to you?",
            "What questions do you have about how the coverage works?"
        ],
        talking_points=[
            "HomeProtector insurance is designed specifically for your RBC mortgage, with benefits paid directly to your mortgage balance.",
            "You can choose coverage for life, disability, critical illness, or a combination based on your needs.",
            "The application process is simple and can be completed right now as part of your mortgage setup.",
            "Coverage begins as soon as your mortgage is funded, with no waiting period for life insurance benefits."
        ],
        objection_responses={
            "I don't understand how it works": "Let me explain it simply: if you choose life coverage and were to pass away, the insurance would pay off your remaining mortgage balance. For disability, it would cover your mortgage payments while you're unable to work. For critical illness, it provides a lump sum payment of either 100% or 25% of your mortgage balance depending on the condition.",
            
            "I'm healthy, I don't need it": "I'm glad to hear you're in good health! However, protection is about preparing for unexpected events. Many of our clients who make claims never expected to need the coverage, but were grateful to have it when the unexpected occurred.",
            
            "I'll get better rates elsewhere": "You might want to compare rates, which is understandable. However, HomeProtector is conveniently integrated with your mortgage, doesn't require a medical exam for coverage up to $500,000, and the benefits are paid directly to your mortgage. These features often make it the most straightforward option."
        }
    )

def get_what_if_scenario_template() -> ConversationTemplate:
    """Get template for discussing 'what if' scenarios"""
    return ConversationTemplate(
        title="What If Protection Scenarios",
        description="Exploring specific scenarios that could impact mortgage payments",
        objective="Help client visualize the impact of different life events on their mortgage and how protection helps",
        key_questions=[
            "What would happen to your mortgage if you were unable to work for 6 months?",
            "Who would be responsible for the mortgage if something happened to you?",
            "How would a critical illness diagnosis affect your financial situation?",
            "Have you experienced job loss before, and how did it impact your finances?"
        ],
        talking_points=[
            "Let's look at some specific numbers for your situation to see the potential impact.",
            "Many people underestimate the likelihood of disability during their working years.",
            "Critical illness can bring both medical expenses and income loss at the same time.",
            "Protection gives you one less thing to worry about during an already stressful time."
        ],
        objection_responses={
            "My spouse could cover the payments": "That's good to have that backup. Have you calculated if your spouse's income alone could cover all household expenses including the mortgage? Many families find there would still be a shortfall, especially with potential additional expenses.",
            
            "I have savings for emergencies": "Emergency savings are essential, but how many months could they last? The average disability lasts over 2.5 years, which would deplete most people's savings. Protection can help preserve those savings for other needs.",
            
            "I don't believe I'll get sick": "I hope that's true! But statistics show that 1 in 3 Canadians will experience a disability lasting 90 days or more before age 65. Protection is about preparing for possibilities, not predictions."
        }
    )

def create_personalized_guide(
    client_data: Dict[str, Any],
    journey_stage: MortgageJourneyStage,
    life_events: List[LifeEvent] = None
) -> PersonalizedGuide:
    """
    Create a personalized conversation guide based on client data,
    current mortgage journey stage, and any recent life events
    """
    # Select appropriate template based on journey stage
    stage_info = get_journey_stage_description(journey_stage)
    
    if journey_stage in [MortgageJourneyStage.INITIAL_INQUIRY, MortgageJourneyStage.RATE_SHOPPING]:
        template = get_discovery_conversation_template()
        timing = "During initial client meeting or rate discussion"
    elif journey_stage in [MortgageJourneyStage.DOCUMENTATION_COLLECTION, MortgageJourneyStage.APPLICATION_SUBMISSION]:
        template = get_protection_benefits_template()
        timing = "While collecting documents or preparing application"
    else:
        template = get_what_if_scenario_template()
        timing = "During approval review or closing preparation"
    
    # Generate client-specific talking points
    client_specific_points = []
    
    # Add points based on client profile
    if client_data.get("dependents", 0) > 0:
        client_specific_points.append(
            f"With {client_data.get('dependents')} dependents, ensuring they can stay in your home if something happens to you is especially important."
        )
    
    if client_data.get("mortgage_amount", 0) > 500000:
        client_specific_points.append(
            f"With a mortgage of ${client_data.get('mortgage_amount'):,.2f}, the financial impact of an unexpected event could be significant."
        )
    
    if client_data.get("age", 35) > 45:
        client_specific_points.append(
            "As we get older, the risk of health issues increases, making protection increasingly valuable."
        )
    
    # Add points based on life events
    if life_events:
        for event in life_events:
            talking_points = get_life_event_protection_talking_points(event)
            if talking_points and len(talking_points) > 0:
                client_specific_points.append(random.choice(talking_points))
    
    # Generate next steps based on journey stage
    if journey_stage in [MortgageJourneyStage.INITIAL_INQUIRY, MortgageJourneyStage.RATE_SHOPPING]:
        next_steps = [
            "Schedule follow-up to discuss protection in more detail",
            "Send client information about protection options",
            "Note client's initial concerns for future discussions"
        ]
    elif journey_stage in [MortgageJourneyStage.DOCUMENTATION_COLLECTION, MortgageJourneyStage.APPLICATION_SUBMISSION]:
        next_steps = [
            "Complete protection application if client is interested",
            "Address any specific questions about coverage",
            "Include protection details in mortgage application"
        ]
    else:
        next_steps = [
            "Finalize protection choices before closing",
            "Ensure client understands when coverage begins",
            "Provide confirmation of protection details"
        ]
    
    return PersonalizedGuide(
        template=template,
        client_specific_points=client_specific_points,
        recommended_timing=timing,
        next_steps=next_steps
    )

def get_objection_handling_tips() -> Dict[str, List[str]]:
    """
    Get comprehensive objection handling tips for common client concerns
    """
    return {
        "cost": [
            "Compare the monthly premium to everyday expenses (coffee, streaming services) to put the cost in perspective",
            "Calculate the cost as a percentage of their mortgage payment (often just 5-10%)",
            "Explain that premiums are fixed for the life of the coverage, unlike many other insurance products",
            "Show the actual numbers for their specific situation rather than speaking generally"
        ],
        "existing_coverage": [
            "Ask about the specific amount and type of existing coverage to identify potential gaps",
            "Explain how mortgage protection complements rather than replaces existing coverage",
            "Discuss the convenience of having mortgage-specific protection that pays directly to the mortgage",
            "Calculate whether their existing coverage would be sufficient for all needs including mortgage payments"
        ],
        "not_now": [
            "Explain that health issues could affect future insurability, so it's best to secure coverage while healthy",
            "Point out that the application process is simplest when done alongside the mortgage",
            "Remind them that coverage begins immediately upon mortgage funding",
            "Discuss how protection decisions are often postponed and then forgotten until it's too late"
        ],
        "won't_happen_to_me": [
            "Share relevant statistics about disability, critical illness, or job loss without being alarmist",
            "Tell stories (anonymized) about clients who benefited from having protection",
            "Acknowledge their optimism while gently introducing the concept of preparing for possibilities",
            "Focus on protection as a way to maintain control in unpredictable situations"
        ],
        "complicated": [
            "Break down the coverage options one at a time rather than presenting everything at once",
            "Use the WIPT calculator to show specific scenarios with actual numbers",
            "Provide simple, one-page explanations of each coverage type",
            "Compare to familiar concepts (like how home insurance protects against rare but significant events)"
        ]
    }

def get_timing_recommendations() -> Dict[str, Dict[str, Any]]:
    """
    Get recommendations for when to discuss protection based on different scenarios
    """
    return {
        "ideal_timing": {
            "description": "The ideal time to discuss protection in depth",
            "primary_stage": MortgageJourneyStage.DOCUMENTATION_COLLECTION,
            "rationale": "Client is already providing financial information, making it natural to discuss financial protection. Early enough in the process to not feel rushed, but after client has committed to proceeding with the mortgage.",
            "approach": "Integrate protection discussion naturally while reviewing financial documents: 'Now that we're looking at your overall financial picture, let's discuss how to protect this investment.'"
        },
        "early_mention": {
            "description": "When to first introduce the concept of protection",
            "primary_stage": MortgageJourneyStage.INITIAL_INQUIRY,
            "rationale": "Plants the seed early so protection doesn't come as a surprise later. Allows client time to consider the concept before making a decision.",
            "approach": "Brief, natural mention: 'As we move forward, we'll also discuss options to protect your mortgage investment. It's an important part of the overall financial picture.'"
        },
        "last_opportunity": {
            "description": "Final chance to add protection easily",
            "primary_stage": MortgageJourneyStage.CLOSING,
            "rationale": "Last opportunity to add protection without requiring a separate application process after mortgage is funded.",
            "approach": "Direct but not pushy: 'Before we finalize everything, I want to ensure you've made an informed decision about protection options. After today, adding protection would require a separate application.'"
        },
        "life_event_triggered": {
            "description": "When to discuss based on client life events",
            "rationale": "Certain life events create natural opportunities to discuss protection as needs and priorities change.",
            "events": {
                LifeEvent.NEW_CHILD: "When a client mentions a new child, it's a perfect time to discuss protection as family responsibilities increase.",
                LifeEvent.CAREER_CHANGE: "Job changes often mean changes in benefits coverage, creating a natural opportunity to discuss mortgage protection.",
                LifeEvent.HEALTH_CHANGE: "Recent health concerns, even minor ones, can make clients more receptive to protection discussions."
            }
        }
    }
