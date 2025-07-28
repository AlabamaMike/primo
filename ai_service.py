"""
AI Service for task name suggestions and completion
"""
import os
import asyncio
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
import logging

# Set up logging
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

class AITaskAssistant:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the AI Task Assistant
        
        Args:
            api_key: OpenAI API key (if None, will look for OPENAI_API_KEY environment variable)
            model: OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
    
    def is_enabled(self) -> bool:
        """Check if AI assistance is enabled (API key is available)"""
        return self.client is not None
    
    async def suggest_task_names(self, partial_input: str, context: Optional[Dict] = None) -> List[str]:
        """
        Generate task name suggestions based on partial input
        
        Args:
            partial_input: The partial task name/description entered by user
            context: Optional context (user's existing tasks, priority, etc.)
            
        Returns:
            List of suggested task names
        """
        if not self.is_enabled():
            return []
        
        try:
            # Build context information
            context_info = ""
            if context:
                if context.get("existing_tasks"):
                    context_info += f"User's recent tasks: {', '.join(context['existing_tasks'][:5])}\n"
                if context.get("priority"):
                    context_info += f"Priority level: {context['priority']}\n"
                if context.get("project"):
                    context_info += f"Project context: {context['project']}\n"
            
            # Create the prompt
            system_prompt = """You are a helpful AI assistant that suggests task names for a task management application. 
Your job is to provide concise, actionable task names based on user input.

Guidelines:
- Suggest 3-5 task names maximum
- Keep suggestions under 50 characters
- Make them specific and actionable
- Use action verbs when appropriate
- Consider the user's context and existing tasks
- Return only the task names, one per line
- No numbers, bullets, or extra formatting"""

            user_prompt = f"""Based on this partial input: "{partial_input}"
{context_info}
Suggest relevant task names:"""

            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=10.0
            )
            
            # Parse response
            suggestions = response.choices[0].message.content.strip().split('\n')
            suggestions = [s.strip() for s in suggestions if s.strip()]
            
            # Clean and limit suggestions
            clean_suggestions = []
            for suggestion in suggestions[:5]:  # Max 5 suggestions
                # Remove any numbering or formatting
                cleaned = suggestion.strip('- ').strip('1234567890. ').strip()
                if cleaned and len(cleaned) <= 100:  # Reasonable length limit
                    clean_suggestions.append(cleaned)
            
            return clean_suggestions[:5]  # Return max 5 suggestions
            
        except Exception as e:
            print(f"Error generating task suggestions: {e}")
            return []
    
    async def expand_task_description(self, task_title: str, brief_description: str = "") -> str:
        """
        Generate a detailed task description based on the title and brief description
        
        Args:
            task_title: The task title
            brief_description: Optional brief description
            
        Returns:
            Expanded task description
        """
        if not self.is_enabled():
            return brief_description
        
        try:
            system_prompt = """You are a helpful AI assistant that helps expand task descriptions. 
Given a task title and optional brief description, provide a clear, detailed description that includes:
- What needs to be done
- Key steps or considerations
- Expected outcome

Keep the description practical and under 200 characters."""

            user_prompt = f"""Task Title: "{task_title}"
Brief Description: "{brief_description}"

Provide a detailed task description:"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.7,
                timeout=10.0
            )
            
            expanded_description = response.choices[0].message.content.strip()
            
            # Ensure it's not too long
            if len(expanded_description) > 250:
                expanded_description = expanded_description[:247] + "..."
            
            return expanded_description
            
        except Exception as e:
            print(f"Error expanding task description: {e}")
            return brief_description
    
    async def suggest_task_breakdown(self, task_title: str, description: str = "") -> List[str]:
        """
        Break down a complex task into smaller subtasks
        
        Args:
            task_title: The main task title
            description: Optional task description
            
        Returns:
            List of subtask suggestions
        """
        if not self.is_enabled():
            return []
        
        try:
            system_prompt = """You are a helpful AI assistant that breaks down complex tasks into smaller, manageable subtasks.
Provide 3-7 specific, actionable subtasks that would help complete the main task.
Each subtask should be:
- Specific and actionable
- Under 50 characters
- A logical step toward completing the main task

Return only the subtask names, one per line."""

            user_prompt = f"""Main Task: "{task_title}"
Description: "{description}"

Break this down into subtasks:"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7,
                timeout=10.0
            )
            
            subtasks = response.choices[0].message.content.strip().split('\n')
            subtasks = [s.strip() for s in subtasks if s.strip()]
            
            # Clean and limit subtasks
            clean_subtasks = []
            for subtask in subtasks[:7]:  # Max 7 subtasks
                cleaned = subtask.strip('- ').strip('1234567890. ').strip()
                if cleaned and len(cleaned) <= 80:
                    clean_subtasks.append(cleaned)
            
            return clean_subtasks
            
        except Exception as e:
            print(f"Error generating task breakdown: {e}")
            return []

# Global AI assistant instance
ai_assistant = AITaskAssistant()

async def get_task_suggestions(partial_input: str, user_context: Optional[Dict] = None) -> List[str]:
    """
    Convenience function to get task suggestions
    """
    return await ai_assistant.suggest_task_names(partial_input, user_context)

async def expand_description(task_title: str, brief_description: str = "") -> str:
    """
    Convenience function to expand task description
    """
    return await ai_assistant.expand_task_description(task_title, brief_description)

async def breakdown_task(task_title: str, description: str = "") -> List[str]:
    """
    Convenience function to break down a task
    """
    return await ai_assistant.suggest_task_breakdown(task_title, description)
