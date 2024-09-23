from typing import List, Optional, Union
 
from pydantic import BaseModel
 
 
class NumberOfReactionsModel(BaseModel):
    like: int
    dislike: int
    share: int
    flag: int
 
 
class CurrentSourceModel(BaseModel):
    sourceID: str
    credibility: float
    followers: float
    remainingUses: int
 
 
class NumberOfReactionsCommentModel(BaseModel):
    like: int
    dislike: int
 
 
class CommentsModel(BaseModel):
    numberOfReactions: NumberOfReactionsCommentModel
 
 
class CurrentPostModel(BaseModel):
    postID: str
    numberOfReactions: NumberOfReactionsModel
    comments: List[CommentsModel]
    shown: bool
 
 
class StatesModel(BaseModel):
    currentSource: CurrentSourceModel
    currentPost: CurrentPostModel
 
 
class TimerModel(BaseModel):
    firstShowTime: int
    lastShowTime: Optional[int]
    lastHideTime: Optional[int]
    visibleDuration: int
    firstInteractTime: Optional[int]
    lastInteractTime: Optional[int]
 
 
class PostReactionsModel(BaseModel):
    postID: Optional[int]
    reactions: List[str]
    timer: Optional[TimerModel]
 
 
class CommentReactionsModel(BaseModel):
    commentID: int
    reactions: List[str]
    timer: TimerModel
 
 
class InteractionsModel(BaseModel):
    postReactions: List[Union[PostReactionsModel, str]]
    commentReactions: List[CommentReactionsModel]
    comment: Optional[str]
    timer: TimerModel
 
 
class ParticipantModel(BaseModel):
    participantID: str
    credibility: float
    followers: float
    interactions: List[InteractionsModel]
    credibilityHistory: List[float]
    followerHistory: List[float]
 
 
class JSONResultModel(BaseModel):
    studyID: str
    studyModTime: int
    sessionID: str
    startTime: int
    endTime: int
    states: List[StatesModel]
    participant: ParticipantModel
    completionCode: str
    savedResults: bool