# Hydra Trainer

A package that wraps Hugging Face's Transformer Trainer with Hydra integration for better configuration management and hyperparameter optimization support.

Checkout my [powerformer repo](https://github.com/emapco/powerformer) for a concrete example.

## Features

- Hydra configuration management
- Optuna hyperparameter optimization integration
- Easy-to-extend base classes for custom datasets and trainers
- Specify TrainingArguments or hyperparameter search parameters within a hydra configuration file
  - An example config, `base.yaml`, is provided in this package.

## Installation

```bash
pip install hydra-trainer
```

## Quick Start

1. Create your dataset class by extending `BaseDataset` or use any dataset that extends `datasets.Dataset`:

```python:example.py
from typing import Literal
from omegaconf import DictConfig
from hydra_trainer import BaseDataset

class ExampleDataset(BaseDataset):
    def __init__(self, cfg: DictConfig, dataset_key: Literal["train", "eval"]):
        super().__init__(cfg)
        self.dataset_key = dataset_key
        # TODO: implement dataset loading and preprocessing
        raise NotImplementedError

    def __len__(self):
        # TODO: implement this method
        raise NotImplementedError

    def __getitem__(self, idx):
        # TODO: implement this method
        raise NotImplementedError
```

2. Create your trainer class by extending `BaseTrainer`:

```python:example.py
from typing import Literal

import optuna
from omegaconf import DictConfig

from hydra_trainer import BaseTrainer


class ExampleTrainer(BaseTrainer[ExampleDataset, DictConfig]):
    def model_init_factory(self):
        def model_init(trial: optuna.Trial | None = None):
            model_cfg = self.get_trial_model_cfg(trial, self.cfg)
            # TODO: implement model initialization
            raise NotImplementedError

        return model_init

    def dataset_factory(
        self, dataset_cfg: DictConfig, dataset_key: Literal["train", "eval"]
    ) -> ExampleDataset:
        # TODO: implement this method
        raise NotImplementedError
```

3. Set up your training script with Hydra:

```python:example.py
import hydra
from omegaconf import DictConfig

@hydra.main(config_path="hydra_trainer", config_name="base", version_base=None)
def main(cfg: DictConfig):
    trainer = ExampleTrainer(cfg)
    trainer.train()

if __name__ == "__main__":
    main()
```

## BaseTrainer Key Features

1. **Model Initialization Factory**: Implement `model_init_factory()` to define how your model is created.
2. **Dataset Factory**: Implement `dataset_factory()` to create your training and evaluation datasets

## Configuration

The package uses Hydra for configuration management. Here's the base configuration structure:

```yaml
seed: 42
checkpoint_path: null
resume_from_checkpoint: null
do_hyperoptim: false
early_stopping_patience: 3

model: # model parameters - access them within `model_init_factory` implementation
  d_model: 128
  n_layers: 12
  n_heads: 16
  d_ff: 512

trainer: #  transformers.TrainingArguments
  num_train_epochs: 3
  eval_strategy: steps
  eval_steps: 50
  logging_steps: 5
  output_dir: training_output
  per_device_train_batch_size: 2
  per_device_eval_batch_size: 4096
  learning_rate: 5e-3
  weight_decay: 0.0
  fp16: true

hyperopt:
  n_trials: 128
  patience: 2
  persistence: true # set to false to use in memory storage instead of db storage
  load_if_exists: true
  storage_url: postgresql://postgres:password@127.0.0.1:5432/postgres
  storage_heartbeat_interval: 15
  storage_engine_kwargs:
    pool_size: 5
    connect_args:
      keepalives: 1
  hp_space:
    training:
      - name: learning_rate # TrainingArguments attribute name
        type: float
        low: 5e-5
        high: 5e-3
        step: 1e-5
        log: true
    model:
      - name: d_model # model parameters
        type: int
        low: 128
        high: 512
        step: 128
        log: true
```

## Hyperparameter Optimization

Enable hyperparameter optimization by setting `do_hyperoptim: true` in your config. The package uses Optuna for hyperparameter optimization with support for:

- Integer parameters
- Float parameters
- Categorical parameters
- Persistent storage with a relational database
- Early stopping with patient pruning
