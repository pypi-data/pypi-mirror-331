from .GenericNode import GenericNode
from .OpenaiNode import OpenAINode
from .AggregateNode import AggregateNode
from .IfNode import IfNode
from .ClaudeNode import ClaudeNode
from .ListNode import ListNode
from .FilterNode import FilterNode
from .RequestNode import RequestNode
from .StartNode import StartNode
from .SlackNode import SlackNode
from .base_node import BaseNode
from .Neo4jNode import Neo4jNode
from .DynamodbNode import DynamodbNode





# You can also include a registry for all nodes if needed
NODES = {
    "Slack": SlackNode,
    "OpenAI": OpenAINode,
    "Aggregate": AggregateNode,
    "If": IfNode,
    "Claude": ClaudeNode,
    "List": ListNode,
    "Filter": FilterNode,
    "Request": RequestNode,
    "Start": StartNode,
    "Generic": GenericNode,
    "base": BaseNode,
    "Neo4j": Neo4jNode,
    "Dynamodb": DynamodbNode

}