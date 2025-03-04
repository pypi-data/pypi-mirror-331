from typing import Literal

import hydra
import optuna
from omegaconf import DictConfig

from hydra_trainer import BaseDataset, BaseTrainer


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


@hydra.main(config_path="hydra_trainer", config_name="base", version_base=None)
def main(cfg: DictConfig):
    trainer = ExampleTrainer(cfg)
    trainer.train()


if __name__ == "__main__":
    main()
