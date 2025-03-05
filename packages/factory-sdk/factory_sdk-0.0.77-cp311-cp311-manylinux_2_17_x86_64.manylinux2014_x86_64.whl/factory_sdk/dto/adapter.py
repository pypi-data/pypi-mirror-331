from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
    FactoryRevisionRef,
)
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from enum import Enum
from typing import Union


class InitArgs(BaseModel):
    n_test_samples: int = Field(
        1000,
        description="The number of samples to used for layer selection and rank estimation",
    )


class AdapterArgs(BaseModel):
    # could be int or "auto"
    rank: Union[int, str] = Field("auto", description="The rank of the adapter")
    alpha: Union[int, str] = Field("auto", description="The alpha of the adapter")
    dropout: float = Field(0.1, description="The dropout to use for the lora model")
    layer_selection_percentage: float = Field(
        0.5, description="The percentage of layers to select for training", gt=0, le=1
    )
    target_modules: Optional[List[str]] = Field(
        None, description="The target modules to train"
    )


class TrainArgs(BaseModel):
    train_batch_size: int = Field(8, description="The batch size to use for training")
    eval_batch_size: int = Field(8, description="The batch size to use for evaluation")
    eval_every_n_minutes: int = Field(
        10,
        description="The number of minutes to wait bevore evaluating and checkpointing",
    )
    gradient_accumulation_steps: int = Field(
        1, description="The number of gradient accumulation steps"
    )
    max_eval_samples: int = Field(
        1000, description="The maximum number of samples to evaluate"
    )
    max_train_steps: int = Field(
        -1, description="The maximum number of training steps"
    )

    num_train_epochs: int = Field(3, description="The number of epochs to train")
    learning_rate: float = Field(
        5e-5, description="The learning rate to use for training"
    )
    dtype: str = Field("fp16", description="The dtype to use for training")
    attention_implementation: str = Field(
        "fa2", description="The attention implementation to use for training"
    )
    quantization_bits: Optional[int] = Field(
        4, description="The number of bits to use for quantization"
    )

class AdapterMeta(FactoryResourceMeta):
    pass


class AdapterInitData(FactoryResourceInitData):

    def create_meta(self, tenant_name, project_name) -> AdapterMeta:
        return AdapterMeta(
            name=self.name, project=project_name, tenant=tenant_name, type="adapter"
        )


class AutoTrainingParams(str, Enum):
    AUTO_LORA = "auto_lora"
    AUTO_LORA_FAST = "auto_lora_fast"


class AdapterRevision(FactoryResourceRevision):
    model: Optional[FactoryRevisionRef] = None
    dataset: Optional[FactoryRevisionRef] = None
    recipe: Optional[List[FactoryRevisionRef]] = None
    train_params: Optional[AutoTrainingParams] = None

class AdapterObject(BaseModel):
    meta: AdapterMeta
    revision: str

    def get_revision(self):
        revisions = self.meta.revisions
        revisions = [revision for revision in revisions if revision.id == self.revision]
        if len(revisions) == 0:
            raise Exception("Revision not found")

        return revisions[0]
