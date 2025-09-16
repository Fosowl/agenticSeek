#!/usr/bin/env python3

import os, sys
import uvicorn
import asyncio
import time
from typing import List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid

from sources.llm_provider import Provider
from sources.interaction import Interaction
from sources.agents import CasualAgent, CoderAgent, FileAgent
from sources.utility import pretty_print
from sources.logger import Logger
from sources.schemas import QueryRequest, QueryResponse

api = FastAPI(title="AgenticSeek API", version="0.1.0")
logger = Logger("backend.log")

# Vercel will handle CORS, but this is good for local testing
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Filesystem operations removed for Vercel compatibility

def initialize_system():
    # Replaced config.ini with environment variables for Vercel deployment
    personality_folder = "jarvis" if os.environ.get('JARVIS_PERSONALITY', 'false').lower() == 'true' else "base"
    languages = os.environ.get('LANGUAGES', 'en').split(' ')

    # For Vercel, we must use a remote provider. IS_LOCAL must be False.
    provider = Provider(
        provider_name=os.environ.get("PROVIDER_NAME", "google"),
        model=os.environ.get("PROVIDER_MODEL", "gemini-1.5-flash"),
        server_address=os.environ.get("PROVIDER_SERVER_ADDRESS"), # Not used for most remote providers
        is_local=os.environ.get('IS_LOCAL', 'false').lower() == 'true'
    )
    logger.info(f"Provider initialized: {provider.provider_name} ({provider.model})")

    # Browser functionality is removed for Vercel compatibility

    # BrowserAgent and PlannerAgent are removed as they require a browser
    agents = [
        CasualAgent(
            name=os.environ.get("AGENT_NAME", "AgenticSeek"),
            prompt_path=f"prompts/{personality_folder}/casual_agent.txt",
            provider=provider, verbose=False
        ),
        CoderAgent(
            name="coder",
            prompt_path=f"prompts/{personality_folder}/coder_agent.txt",
            provider=provider, verbose=False
        ),
        FileAgent(
            name="File Agent",
            prompt_path=f"prompts/{personality_folder}/file_agent.txt",
            provider=provider, verbose=False
        ),
    ]
    logger.info("Agents initialized")

    interaction = Interaction(
        agents,
        tts_enabled=os.environ.get('SPEAK', 'false').lower() == 'true',
        stt_enabled=os.environ.get('LISTEN', 'false').lower() == 'true',
        # Session recovery disabled for ephemeral filesystem
        recover_last_session=False,
        langs=languages
    )
    logger.info("Interaction initialized")
    return interaction

interaction = initialize_system()
is_generating = False
query_resp_history = [] # This will reset with each invocation on serverless

# Screenshot endpoint removed for Vercel compatibility

@api.get("/")
async def health_check():
    logger.info("Health check endpoint called")
    # The root of the API should handle this for Vercel
    return {"status": "healthy", "version": "0.1.0"}

# This is the entry point Vercel will use
@api.get("/api/health")
async def health_check_api():
    logger.info("Health check endpoint called")
    return {"status": "healthy", "version": "0.1.0"}

@api.get("/api/is_active")
async def is_active():
    logger.info("Is active endpoint called")
    return {"is_active": interaction.is_active}

@api.get("/api/stop")
async def stop():
    logger.info("Stop endpoint called")
    interaction.current_agent.request_stop()
    return JSONResponse(status_code=200, content={"status": "stopped"})

@api.get("/api/latest_answer")
async def get_latest_answer():
    global query_resp_history
    if interaction.current_agent is None:
        return JSONResponse(status_code=404, content={"error": "No agent available"})
    uid = str(uuid.uuid4())
    if not any(q["answer"] == interaction.current_agent.last_answer for q in query_resp_history):
        query_resp = {
            "done": "false",
            "answer": interaction.current_agent.last_answer,
            "reasoning": interaction.current_agent.last_reasoning,
            "agent_name": interaction.current_agent.agent_name if interaction.current_agent else "None",
            "success": interaction.current_agent.success,
            "blocks": {f'{i}': block.jsonify() for i, block in enumerate(interaction.get_last_blocks_result())} if interaction.current_agent else {},
            "status": interaction.current_agent.get_status_message if interaction.current_agent else "No status available",
            "uid": uid
        }
        interaction.current_agent.last_answer = ""
        interaction.current_agent.last_reasoning = ""
        query_resp_history.append(query_resp)
        return JSONResponse(status_code=200, content=query_resp)
    if query_resp_history:
        return JSONResponse(status_code=200, content=query_resp_history[-1])
    return JSONResponse(status_code=404, content={"error": "No answer available"})

async def think_wrapper(interaction, query):
    try:
        interaction.last_query = query
        logger.info("Agents request is being processed")
        success = await interaction.think()
        if not success:
            interaction.last_answer = "Error: No answer from agent"
            interaction.last_reasoning = "Error: No reasoning from agent"
            interaction.last_success = False
        else:
            interaction.last_success = True
        pretty_print(interaction.last_answer)
        interaction.speak_answer()
        return success
    except Exception as e:
        logger.error(f"Error in think_wrapper: {str(e)}")
        interaction.last_answer = f""
        interaction.last_reasoning = f"Error: {str(e)}"
        interaction.last_success = False
        raise e

@api.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    global is_generating, query_resp_history
    logger.info(f"Processing query: {request.query}")
    query_resp = QueryResponse(
        done="false",
        answer="",
        reasoning="",
        agent_name="Unknown",
        success="false",
        blocks={},
        status="Ready",
        uid=str(uuid.uuid4())
    )
    if is_generating:
        logger.warning("Another query is being processed, please wait.")
        return JSONResponse(status_code=429, content=query_resp.jsonify())

    try:
        is_generating = True
        success = await think_wrapper(interaction, request.query)
        is_generating = False

        if not success:
            query_resp.answer = interaction.last_answer
            query_resp.reasoning = interaction.last_reasoning
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        if interaction.current_agent:
            blocks_json = {f'{i}': block.jsonify() for i, block in enumerate(interaction.current_agent.get_blocks_result())}
        else:
            logger.error("No current agent found")
            blocks_json = {}
            query_resp.answer = "Error: No current agent"
            return JSONResponse(status_code=400, content=query_resp.jsonify())

        logger.info(f"Answer: {interaction.last_answer}")
        logger.info(f"Blocks: {blocks_json}")
        query_resp.done = "true"
        query_resp.answer = interaction.last_answer
        query_resp.reasoning = interaction.last_reasoning
        query_resp.agent_name = interaction.current_agent.agent_name
        query_resp.success = str(interaction.last_success)
        query_resp.blocks = blocks_json
        
        query_resp_dict = {
            "done": query_resp.done,
            "answer": query_resp.answer,
            "agent_name": query_resp.agent_name,
            "success": query_resp.success,
            "blocks": query_resp.blocks,
            "status": query_resp.status,
            "uid": query_resp.uid
        }
        query_resp_history.append(query_resp_dict)

        logger.info("Query processed successfully")
        return JSONResponse(status_code=200, content=query_resp.jsonify())
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        # sys.exit(1) is not ideal for serverless functions
        return JSONResponse(status_code=500, content={"error": f"An unexpected error occurred: {str(e)}"})
    finally:
        logger.info("Processing finished")
        # Session saving is disabled for Vercel's ephemeral filesystem
        # if os.environ.get('SAVE_SESSION', 'false').lower() == 'true':
        #     interaction.save_session()

# The main block is not used on Vercel but good for local testing
if __name__ == "__main__":
    # For local testing, you would need to set environment variables
    uvicorn.run(api, host="0.0.0.0", port=8000)