from fastapi import HTTPException
from src.models.service.chat_models import ChatRequest, AgentResponse
from src.stores import agent_manager_instance, chat_manager_instance
from src.delegator import Delegator
from src.config import setup_logging

logger = setup_logging()


class ChatController:
    def __init__(self, delegator: Delegator):
        self.delegator = delegator

    async def handle_chat(self, chat_request: ChatRequest):
        """Handle chat requests and delegate to appropriate agent"""
        logger.info(f"Received chat request for conversation {chat_request.conversation_id}")

        try:
            # Parse command if present
            agent_name, message = agent_manager_instance.parse_command(chat_request.prompt.content)

            if agent_name:
                agent_manager_instance.set_active_agent(agent_name)
                chat_request.prompt.content = message
            else:
                agent_manager_instance.clear_active_agent()

            # Add user message to chat history
            chat_manager_instance.add_message(chat_request.prompt.dict(), chat_request.conversation_id)

            # If command was parsed, use that agent directly
            if agent_name:
                logger.info(f"Using command agent flow: {agent_name}")
                agent = agent_manager_instance.get_agent(agent_name)
                if not agent:
                    logger.error(f"Agent {agent_name} not found")
                    raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

                agent_response = await agent.chat(chat_request)
                current_agent = agent_name

            # Otherwise use delegator to find appropriate agent
            else:
                logger.info("Using delegator flow")
                # self.delegator.reset_attempted_agents()
                current_agent, agent_response = await self.delegator.delegate_chat(chat_request)

            # We only critically fail if we don't get an AgentResponse
            if not isinstance(agent_response, AgentResponse):
                logger.error(f"Agent {current_agent} returned invalid response type {type(agent_response)}")
                raise HTTPException(status_code=500, detail="Agent returned invalid response type")

            # Convert to API response and add to chat history
            chat_manager_instance.add_response(agent_response.dict(), current_agent, chat_request.conversation_id)

            logger.info(f"Sending response: {agent_response.dict()}")
            return agent_response.dict()

        except HTTPException:
            raise
        except TimeoutError:
            logger.error("Chat request timed out")
            raise HTTPException(status_code=504, detail="Request timed out")
        except ValueError as ve:
            logger.error(f"Input formatting error: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Error in chat route: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # async def get_active_agent_for_chat(self, prompt: dict) -> str:
    #     """Get the active agent for handling the chat request."""
    #     active_agent = agent_manager_instance.get_active_agent()
    #     if active_agent:
    #         return active_agent

    #     logger.info("No active agent, getting delegator response")
    #     result = self.delegator.get_delegator_response(prompt)
    #     logger.info(f"Delegator response: {result}")

    #     if "agent" not in result:
    #         logger.error(f"Missing 'agent' key in delegator response: {result}")
    #         raise ValueError("Invalid delegator response: missing 'agent' key")

    #     return result["agent"]
