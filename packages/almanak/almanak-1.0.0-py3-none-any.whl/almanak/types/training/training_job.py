from typing import List, Union, Optional

from typing_extensions import Literal

from .training_job_wandb_integration_object import TrainingJobWandbIntegrationObject
from ..._models import BaseModel

__all__ = ["TrainingJob", "Error", "Hyperparameters"]


class Error(BaseModel):
    code: str
    """A machine-readable error code."""

    message: str
    """A human-readable error message."""

    param: Optional[str] = None
    """The parameter that was invalid, usually `training_file` or `validation_file`.

    This field will be null if the failure was not parameter-specific.
    """


class Hyperparameters(BaseModel):
    n_epochs: Union[Literal["auto"], int]
    """The number of epochs to train the model for.

    An epoch refers to one full cycle through the training dataset. "auto" decides
    the optimal number of epochs based on the size of the dataset. If setting the
    number manually, we support any number between 1 and 50 epochs.
    """


class TrainingJob(BaseModel):
    id: str
    """The object identifier, which can be referenced in the API endpoints."""

    created_at: int
    """The Unix timestamp (in seconds) for when the training job was created."""

    error: Optional[Error] = None
    """
    For training jobs that have `failed`, this will contain more information on
    the cause of the failure.
    """

    fine_tuned_model: Optional[str] = None
    """The name of the traind model that is being created.

    The value will be null if the training job is still running.
    """

    finished_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the training job was finished.

    The value will be null if the training job is still running.
    """

    hyperparameters: Hyperparameters
    """The hyperparameters used for the training job.

    See the [training guide](https://platform.almanak.com/docs/guides/training)
    for more details.
    """

    model: str
    """The base model that is being traind."""

    object: Literal["training.job"]
    """The object type, which is always "training.job"."""

    organization_id: str
    """The organization that owns the training job."""

    result_files: List[str]
    """The compiled results file ID(s) for the training job.

    You can retrieve the results with the
    [Files API](https://platform.almanak.com/docs/api-reference/files/retrieve-contents).
    """

    seed: int
    """The seed used for the training job."""

    status: Literal[
        "validating_files", "queued", "running", "succeeded", "failed", "cancelled"
    ]
    """
    The current status of the training job, which can be either
    `validating_files`, `queued`, `running`, `succeeded`, `failed`, or `cancelled`.
    """

    trained_tokens: Optional[int] = None
    """The total number of billable tokens processed by this training job.

    The value will be null if the training job is still running.
    """

    training_file: str
    """The file ID used for training.

    You can retrieve the training data with the
    [Files API](https://platform.almanak.com/docs/api-reference/files/retrieve-contents).
    """

    validation_file: Optional[str] = None
    """The file ID used for validation.

    You can retrieve the validation results with the
    [Files API](https://platform.almanak.com/docs/api-reference/files/retrieve-contents).
    """

    estimated_finish: Optional[int] = None
    """
    The Unix timestamp (in seconds) for when the training job is estimated to
    finish. The value will be null if the training job is not running.
    """

    integrations: Optional[List[TrainingJobWandbIntegrationObject]] = None
    """A list of integrations to enable for this training job."""
