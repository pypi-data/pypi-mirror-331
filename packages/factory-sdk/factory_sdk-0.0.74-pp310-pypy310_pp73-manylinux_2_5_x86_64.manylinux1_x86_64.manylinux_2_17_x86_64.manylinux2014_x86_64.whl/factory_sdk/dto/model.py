from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from PIL import Image
from typing import List
from factory_sdk.utils.image import pil_to_datauri
from typing import Any


class ModelArchitecture(str, Enum):
    Gemma2ForCausalLM = "Gemma2ForCausalLM"
    LlamaForCausalLM = "LlamaForCausalLM"
    MistralForCausalLM = "MistralForCausalLM"
    Phi3ForCausalLM = "Phi3ForCausalLM"
    Qwen2ForCausalLM = "Qwen2ForCausalLM"
    #PaliGemmaForConditionalGeneration = "PaliGemmaForConditionalGeneration"
    Phi3VForCausalLM = "Phi3VForCausalLM"

SUPPORTED_ARCHITECTURES=[
"Qwen2ForCausalLM",
"LlamaForCausalLM",
"Gemma2ForCausalLM",
"Phi3ForCausalLM",
"Phi3VForCausalLM"
]

class SupportedModels(str, Enum):
    # meta-llama/Llama-3.2-3B-Instruct
    LLama3_2_Instruct_3B = "meta-llama/Llama-3.2-3B-Instruct"
    # meta-llama/Llama-3.2-1B-Instruct
    LLama3_2_Instruct_1B = "meta-llama/Llama-3.2-1B-Instruct"
    # Qwen/Qwen2.5-0.5B-Instruct
    Qwen2_5_Instruct_0_5B = "Qwen/Qwen2.5-0.5B-Instruct"
    # Qwen/Qwen2.5-1.5B-Instruct
    Qwen2_5_Instruct_1_5B = "Qwen/Qwen2.5-1.5B-Instruct"
    # Qwen/Qwen2.5-3B-Instruct
    Qwen2_5_Instruct_3B = "Qwen/Qwen2.5-3B-Instruct"
    # Qwen/Qwen2.5-7B-Instruct
    Qwen2_5_Instruct_7B = "Qwen/Qwen2.5-7B-Instruct"
    # mistralai/Mistral-7B-Instruct-v0.3
    Mistral7BInstruct = "mistralai/Mistral-7B-Instruct-v0.3"
    # google/gemma-2-2b
    Gemma2_Instruct_2B = "google/gemma-2-2b-it"
    # google/gemma-2-9b-it
    Gemma2_Instruct_9B = "google/gemma-2-9b-it"
    # microsoft/Phi-3.5-mini-instruct
    Phi3_5_Mini_Instruct = "microsoft/Phi-3.5-mini-instruct"
    # google/paligemma2-3b-pt-224
    #PaliGemma_3B_224 = "google/paligemma2-3b-pt-224"
    # google/paligemma2-3b-pt-448
    #PaliGemma_3B_448 = "google/paligemma2-3b-pt-448"
    # google/paligemma2-3b-pt-896
    #PaliGemma_3B_896 = "google/paligemma2-3b-pt-896"
    # manufactAILabs/ModelOne
    ModelOne = "manufactAILabs/ModelOne"
    # microsoft/Phi-3.5-vision-instruct
    Phi3_5_Vision_Instruct = "microsoft/Phi-3.5-vision-instruct"


MODEL2NAME = {
    SupportedModels.LLama3_2_Instruct_3B: "Llama-3.2-3B-Instruct",
    SupportedModels.LLama3_2_Instruct_1B: "Llama-3.2-1B-Instruct",
    SupportedModels.Qwen2_5_Instruct_0_5B: "Qwen2.5-0.5B-Instruct",
    SupportedModels.Qwen2_5_Instruct_1_5B: "Qwen2.5-1.5B-Instruct",
    SupportedModels.Qwen2_5_Instruct_3B: "Qwen2.5-3B-Instruct",
    SupportedModels.Qwen2_5_Instruct_7B: "Qwen2.5-7B-Instruct",
    SupportedModels.Mistral7BInstruct: "Mistral-7B-Instruct",
    SupportedModels.Gemma2_Instruct_2B: "Gemma-2-2B-Instruct",
    SupportedModels.Gemma2_Instruct_9B: "Gemma-2-9B-Instruct",
    SupportedModels.Phi3_5_Mini_Instruct: "Phi-3.5-Mini-Instruct",
    #SupportedModels.PaliGemma_3B_224: "PaliGemma-3B-224",
    #SupportedModels.PaliGemma_3B_448: "PaliGemma-3B-448",
    #SupportedModels.PaliGemma_3B_896: "PaliGemma-3B-896",
    SupportedModels.ModelOne: "ModelOne",
    SupportedModels.Phi3_5_Vision_Instruct: "Phi-3.5-Vision-Instruct",
}

MODEL2ARCH = {
    SupportedModels.LLama3_2_Instruct_3B: ModelArchitecture.LlamaForCausalLM,
    SupportedModels.LLama3_2_Instruct_1B: ModelArchitecture.LlamaForCausalLM,
    SupportedModels.Qwen2_5_Instruct_0_5B: ModelArchitecture.Qwen2ForCausalLM,
    SupportedModels.Qwen2_5_Instruct_1_5B: ModelArchitecture.Qwen2ForCausalLM,
    SupportedModels.Qwen2_5_Instruct_3B: ModelArchitecture.Qwen2ForCausalLM,
    SupportedModels.Qwen2_5_Instruct_7B: ModelArchitecture.Qwen2ForCausalLM,
    SupportedModels.Mistral7BInstruct: ModelArchitecture.MistralForCausalLM,
    SupportedModels.Gemma2_Instruct_2B: ModelArchitecture.Gemma2ForCausalLM,
    SupportedModels.Gemma2_Instruct_9B: ModelArchitecture.Gemma2ForCausalLM,
    SupportedModels.Phi3_5_Mini_Instruct: ModelArchitecture.Phi3ForCausalLM,
    #SupportedModels.PaliGemma_3B_224: ModelArchitecture.PaliGemmaForConditionalGeneration,
    #SupportedModels.PaliGemma_3B_448: ModelArchitecture.PaliGemmaForConditionalGeneration,
    #SupportedModels.PaliGemma_3B_896: ModelArchitecture.PaliGemmaForConditionalGeneration,
    SupportedModels.ModelOne: ModelArchitecture.Phi3VForCausalLM,
    SupportedModels.Phi3_5_Vision_Instruct: ModelArchitecture.Phi3VForCausalLM,
}

ARCH2AUTO = {
    ModelArchitecture.LlamaForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Qwen2ForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.MistralForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Gemma2ForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Phi3ForCausalLM: AutoModelForCausalLM,
    #ModelArchitecture.PaliGemmaForConditionalGeneration: AutoModelForCausalLM,
    ModelArchitecture.Phi3VForCausalLM: AutoModelForCausalLM,
}
ARCH2PROCESSOR = {
    ModelArchitecture.LlamaForCausalLM: AutoTokenizer,
    ModelArchitecture.Qwen2ForCausalLM: AutoTokenizer,
    ModelArchitecture.MistralForCausalLM: AutoTokenizer,
    ModelArchitecture.Gemma2ForCausalLM: AutoTokenizer,
    ModelArchitecture.Phi3ForCausalLM: AutoTokenizer,
    #ModelArchitecture.PaliGemmaForConditionalGeneration: AutoProcessor,
    ModelArchitecture.Phi3VForCausalLM: AutoProcessor,
}


class ModelMeta(FactoryResourceMeta):
    pass


class ModelInitData(FactoryResourceInitData):
    def create_meta(self, tenant_name, project_name=None) -> ModelMeta:
        return ModelMeta(name=self.name, tenant=tenant_name, type="model")


class ModelRevision(FactoryResourceRevision):
    pass


class ModelObject(BaseModel):
    meta: ModelMeta
    revision: str


class InputImage(BaseModel):
    data: str

    @staticmethod
    def from_pil(image: Image) -> "InputImage":
        return InputImage(data=pil_to_datauri(image))


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Role2Int(Enum):
    SYSTEM = 0
    USER = 1
    ASSISTANT = 2

class Message(BaseModel):
    role: Role
    content: str


class ModelChatInput(BaseModel):
    images: Optional[List[Image.Image]] = None
    messages: List[Message] = Field(min_length=1)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Token(BaseModel):
    id: int


class GeneratedToken(Token):
    logprob: float
    rank: int


class MetricScore(BaseModel):
    score: float


class ModelInstance(BaseModel):
    model: Any
    processor: Any
    tokenizer: Any
