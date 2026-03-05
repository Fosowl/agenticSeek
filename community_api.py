#!/usr/bin/env python3

import time
import uuid
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class CommunityCommentCreate(BaseModel):
    content: str
    author: str = "Anonymous"


class CommunityComment(BaseModel):
    id: str
    content: str
    author: str
    created_at: float


class CommunityPostCreate(BaseModel):
    content: str
    author: str = "Anonymous"


class CommunityPost(BaseModel):
    id: str
    content: str
    author: str
    likes: int = 0
    comments: List[CommunityComment] = Field(default_factory=list)
    created_at: float


class QueryRequest(BaseModel):
    query: str
    tts_enabled: bool = False


api = FastAPI(title="AgenticSeek Community API", version="0.1.0-community")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

community_posts: List[CommunityPost] = [
    CommunityPost(
        id=str(uuid.uuid4()),
        content="Welcome to AgenticSeek community. Share your workflows and launch updates.",
        author="AgenticSeek",
        likes=0,
        comments=[],
        created_at=time.time(),
    )
]


@api.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0-community"}


@api.get("/is_active")
async def is_active():
    return {"is_active": False}


@api.get("/latest_answer")
async def latest_answer():
    return {
        "done": "true",
        "answer": "Community mode is active. Chat agents are disabled in this lightweight preview.",
        "reasoning": "",
        "agent_name": "CommunityMode",
        "success": "true",
        "blocks": {},
        "status": "Community preview ready",
        "uid": str(uuid.uuid4()),
    }


@api.post("/query")
async def query(_: QueryRequest):
    return {
        "done": "true",
        "answer": "Community mode only: use the Community Posts section for like/comment testing.",
        "reasoning": "",
        "agent_name": "CommunityMode",
        "success": "true",
        "blocks": {},
        "status": "Community preview ready",
        "uid": str(uuid.uuid4()),
    }


@api.get("/stop")
async def stop():
    return {"status": "stopped"}


@api.get("/community/posts")
async def get_community_posts():
    ordered_posts = sorted(community_posts, key=lambda p: p.created_at, reverse=True)
    return [post.model_dump() for post in ordered_posts]


@api.post("/community/posts")
async def create_community_post(request: CommunityPostCreate):
    content = request.content.strip()
    author = request.author.strip() or "Anonymous"

    if not content:
        raise HTTPException(status_code=400, detail="Post content cannot be empty")

    post = CommunityPost(
        id=str(uuid.uuid4()),
        content=content,
        author=author,
        likes=0,
        comments=[],
        created_at=time.time(),
    )
    community_posts.append(post)
    return post.model_dump()


@api.post("/community/posts/{post_id}/like")
async def like_community_post(post_id: str):
    for post in community_posts:
        if post.id == post_id:
            post.likes += 1
            return {"post_id": post_id, "likes": post.likes}
    raise HTTPException(status_code=404, detail="Post not found")


@api.post("/community/posts/{post_id}/comments")
async def add_community_comment(post_id: str, request: CommunityCommentCreate):
    content = request.content.strip()
    author = request.author.strip() or "Anonymous"

    if not content:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    for post in community_posts:
        if post.id == post_id:
            comment = CommunityComment(
                id=str(uuid.uuid4()),
                content=content,
                author=author,
                created_at=time.time(),
            )
            post.comments.append(comment)
            return comment.model_dump()

    raise HTTPException(status_code=404, detail="Post not found")
