from pydantic import BaseModel
from typing import Optional, List


class AccountData(BaseModel):
    profileBannerUrl: Optional[str] = None
    profileImageUrl: Optional[str] = None
    description: Optional[str] = None
    userSince: str
    location: Optional[str] = None
    name: str


class Account(BaseModel):
    id: int
    username: str
    data: AccountData
    followerCount: int
    followingCount: int
    isVerified: bool


class Mention(BaseModel):
    id: int
    type: str
    content: str
    originalUrl: Optional[str] = None
    data: Optional[str] = None
    likeCount: int
    quoteCount: int
    replyCount: int
    repostCount: int
    viewCount: int
    mentionedAt: str
    bookmarkCount: int
    account: Account


class MentionsResponse(BaseModel):
    success: bool
    data: List[Mention]


class MentionMetrics(BaseModel):
    view_count: int
    repost_count: int
    reply_count: int
    like_count: int


class TopMention(BaseModel):
    id: int
    content: str
    mentioned_at: str
    metrics: MentionMetrics


class TopMentionsData(BaseModel):
    pageSize: int
    page: int
    total: int
    data: List[TopMention]


class TopMentionsResponse(BaseModel):
    success: bool
    data: TopMentionsData


class TrendingToken(BaseModel):
    change_percent: float
    previous_count: int
    current_count: int
    token: str


class TrendingTokensData(BaseModel):
    pageSize: int
    page: int
    total: int
    data: List[TrendingToken]


class TrendingTokensResponse(BaseModel):
    success: bool
    data: TrendingTokensData


class AccountSmartStats(BaseModel):
    followerEngagementRatio: float
    averageEngagement: float
    smartFollowingCount: int


class AccountSmartStatsResponse(BaseModel):
    success: bool
    data: AccountSmartStats
