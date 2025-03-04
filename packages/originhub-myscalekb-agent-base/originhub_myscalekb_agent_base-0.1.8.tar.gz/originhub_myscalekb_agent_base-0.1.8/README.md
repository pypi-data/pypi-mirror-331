# MyScaleKB Agent Base

MyScaleKB Agent Base 是 MyScaleKB Agent 低代码二次开发框架的基类 Package. 它开源了框架中部分核心基类的具体实现，并以开源
Package 的方式方便 Developer 进行集成和二次开发。

阅读本文档以了解 MyScaleKB Agent Base 中的基础概念。阅读 [MySaleKB Agent Plugin 使用指南](!https://github.com/myscale/myscalekb-agent-plugin/blob/main/README.md) 以了解如何开发并集成部署 MyScaleKB Agent.

## MyScaleKB Agent 低代码二次开发框架

### 介绍

MyScaleKB Agent 低代码二次开发框架是一个创新的平台，旨在填补当前 AI Agent 开发中的技术鸿沟。在现有的 AI
框架生态中，开发者面临着两难境地：底层框架过于复杂，需要深入的技术 expertise；而简单框架又难以满足复杂的业务场景。
MyScaleKB Agent 框架应运而生，为开发者提供了一个灵活且高效的中间解决方案。它允许开发者使用 Python 代码直接定义 Agent
的核心逻辑，无论是数据访问还是 Prompt Engineering。框架的独特之处在于，它不仅仅是一个开发工具，更是一个全方位的 AI 应用交付平台。
开发者可以专注于业务逻辑本身，而框架则负责处理复杂的技术细节。最终交付的不仅仅是一个简单的 Agent，而是一个完整的企业级 AI
应用，包括：

- 低代码实现复杂多 Agent 的群体智能
- 产品化的 Web 用户界面
- 标准化的 OpenAPI 接口
- 基于 MyScaleTelemetry 的应用性能追踪、可持续调优与可视化
  这个框架的设计理念是降低 AI 应用开发的门槛，同时保持足够的灵活性和专业性，使开发者能够快速将创新想法转化为可用的 AI
  解决方案。

### Graph / @node / @edge

Graph 是 Agent Workflow 的一种直观表现形式，例如一个最简单的 RAG 流程可以被表述为 understand -> retrieve -> summarize,
每一个步骤都由一个 node 去执行具体的逻辑，步骤的连接则用 edge 来控制。
@node / @edge 是 MyScaleKB Agent 提供的一种图构建的便捷方式，通过 Python 装饰器的特性，可以快速地构建一个 Graph，例如上面提到的简化
RAG 流程：

```python
class SimpleRag(SubAgent):

    @node
    @edge(target_node="retrieve")
    async def understand(self, data):
        """run llm to get queries from user input"""

    @node
    @edge(target_node="summary")
    async def retrieve(self, data):
        """use retriever to search contexts by queries"""

    @node
    @edge(target_node="__end__")
    async def summarize(self, data):
        """summarize contexts and answer user input"""
```

除了 @node / @edge 之外，MyScaleKB Agent 还提供了 @conditional_edge 来进行有条件的路径控制。

### SubAgent & MultipleAgents Team

有 SubAgent 自然有 MasterAgent，在结构上，MasterAgent 是一个更大的 Graph，SubAgent 即是 MasterAgent 上的一个 node，所以在实现一个
SubAgent 时会以抽象方法的形式要求实现 name() / description()，这对于 MasterAgent 判断某一个 Task/Query 交由哪一个
SubAgent 去执行是起到控制作用的。

```python
class SubAgent(ABC, GraphBuilder):
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Subclasses must implement this method to register with the MasterAgent."""

    raise NotImplementedError

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """Subclasses must implement this method to register with the MasterAgent."""
        raise NotImplementedError
```

### 依赖管理

开发一个 Agent 需要一些必要的工具组件，如 LLM / Embeddings / VectorDataBase 等等，SubAgent 对这些基础组件做了统一的依赖注入：

```python
class SubAgent(ABC, GraphBuilder):
    def __init__(
        self,
        ctx: Context,
        llm: LLM,
        memory: MyScaleChatMemory,
        *args,
        **kwargs,
    ):
        logger.info("Initializing SubAgent - %s", self.__class__.__name__)

        self.llm: ChatOpenAI = llm.model
        self.embedding_model: EmbeddingModel = ctx.embedding_model
        self.myscale_client: Client = ctx.myscale_client
        self.memory = memory
        self.knowledge_scopes = ctx.variables.get("knowledge_scopes")


class SimpleRag(SubAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # other custom component init
```

在实现 `SimpleRag` 时，无需关心 llm / embedding_model 这些内容如何被初始化，它们会由 MyScaleKB Agent
框架去完成依赖管理。这一部分更详细的介绍内容可以通过 `SubAgentRegistry` 进行了解。

### Retriever / Prompt

LLM / Embeddings 是只需要配置即可开箱即用的组件，而 Retriever / Prompt 则是 Agent 实现中主要业务逻辑存在的部分：

- Retriever 控制数据如何检索
- Prompt 控制 LLM 如何被驱动

这两部分在 MyScaleKB Agent 的框架中只提供基类，开发者可以在其实现的 SubAgent 中实例化自定义的 Retriever 和
Prompt，例如上文提到得到 `SimpleRag`，我们为其实现一个 Retriever 和 Prompt.

Retriever 基类从 SubAgent 传递了基础组件的依赖，并定义了一个 retrieve 标准接口。

```python
class Retriever(ABC):
    """Retriever is flexible in use. You can implement a custom Retriever to complete any data query.
    You can use the embedding_model / myscale_client and other components managed by `SubAgent` to conveniently
    instantiate a Retriever.
    """

    def __init__(
        self, embedding_model: EmbeddingModel, myscale_client: Client, knowledge_scopes: List[KnowledgeScope] = None
    ):
        self.embedding_model = embedding_model

    self.myscale_client = myscale_client
    self.knowledge_scopes = knowledge_scopes

    @abstractmethod
    async def retrieve(
        self,
        queries: List[str],
        format_output: Optional[Callable[[List], Any]] = None,
        *args,
        **kwargs,
    ):


class SimpleRagRetriever(Retriever):

    async def retrieve(
        self,
        queries: List[str],
        format_output: Optional[Callable[[List], Any]] = None,
        *args,
        **kwargs,
    ):
        """retrieve workflow:
        1. embed query
        2. use distance(VectorSearch) to query MyScale
        """
```

Prompt 基类也从 SubAgent 传递了它所需要的基础组件的依赖用于管理 Memory，鉴于 Prompt 撰写的灵活性，基类没有定义标准的接口，而是提供工具方法协助子类来管理
user_query 以及 history_messages .

```python
class Prompt(ABC):
    """Base class for prompts."""

    def __init__(self, memory: MyScaleChatMemory):
        self.memory = memory

    def prompt_template(
        self,
        messages: List[BaseMessage],
        with_history: bool = False,
        with_user_query: bool = False,
        with_agent_scratchpad: bool = False,
    ) -> ChatPromptTemplate:


class SimpleRagPrompt(Prompt):

    def understand_prompt_template(self):
        system_prompt = """You are an intelligent assistant integrated with a Retrieval-Augmented Generation (RAG) system and various specialized tools. 

Your primary task is to answer user queries by retrieving relevant information exclusively from a predefined set of
documents available to you.
Utilize the tools at your disposal to enhance the accuracy and relevance of your responses.
"""
        messages = [SystemMessage(content=system_prompt)]
        return self.prompt_template(messages, with_history=True, with_user_query=True)

    def summarize_prompt_template(self, contexts: str):
        system_prompt = """You are an intelligent assistant integrated with a Retrieval-Augmented Generation (RAG) system. 

Your primary task is to answer user queries by retrieved relevant contexts available to you.

Below are the contexts available to you:
{contexts}

Exclude any information that is not directly relevant to the question, and avoid redundancy.
Clearly state "information is missing on [topic]" if the provided contexts do not contain enough information to fully
answer the question.
And recommend more suitable questions to users based on the questions and context.
"""

        messages = [SystemMessage(content=system_prompt.format(contexts=contexts))]
        return self.prompt_template(messages, with_history=True, with_user_query=True)
```

上述 SimpleRag 代码中的 Prompt 仅用于示例。

### Tool

Tool 由 LLM 来选择调用并生成调用参数，并由 Agent 来处理 Tool 的执行结果。在上文的 SimpleRag 中，retrieve 步骤其实就是一个
Tool 的执行，LLM 会基于用户问题为 retrieve 步骤生成恰当的 query 参数。
在 MyScaleKB Agent 的框架中，开发者可以基于 BaseTool 定义任意数量的 Tool：

```python
class BaseTool(ABC):
    """Base class for all tools"""

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Subclasses must implement this method to define the tool name."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """Subclasses must implement this method to define the tool description."""
        raise NotImplementedError

    @abstractmethod
    def params(self) -> Type[BaseModel]:
        """Subclasses must implement this method to define the tool parameters."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Subclasses must implement this method to define the tool execution method."""
        raise NotImplementedError
```

为了让 LLM 理解 Tool 的作用，一个 Tool 必须具有 name 与 description，并且基于 pydantic 定义结构化的调用参数列表，也就是
params. 具体的执行步骤则需要实现 execute，而通常 Tool 的执行会涉及到 retrieve 逻辑，BaseTool 约定了需要 Rertriever 作为构造参数。