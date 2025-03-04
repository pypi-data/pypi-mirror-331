import os
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.preprocessing import minmax_scale
import torch
from torch.utils.data import Dataset, DataLoader
import lightning.pytorch as pl

from .deconvolution._lightning_module import ModelModule

scDeconv_path = Path(os.getenv("SCDECONV_FOLDER", default = str(Path.home() / ".scDeconv")))


class Model:
    _model_cls = ModelModule
    
    def __init__(self, model: ModelModule, device: Literal["cpu", "gpu"] = "gpu") -> None:
        self.model = model
        self.reference = self.model.reference.copy(deep=True)
        
        self.trainer = pl.Trainer(enable_checkpointing=False, logger=False, accelerator=device)
        
    
    @classmethod
    def load(
        cls, 
        organ: str | None = None,
        ckpt_path: str | Path | None = None,
        map_location: str = "cpu",
        device: Literal["cpu", "gpu"] = "gpu",
    ):
        if organ is None and ckpt_path is None:
            raise ValueError("Error!")
        if ckpt_path is None:
            ckpt_path = scDeconv_path.joinpath(f"{organ}.ckpt")
        if isinstance(ckpt_path, str):
            ckpt_path = Path(ckpt_path)
        if not ckpt_path.exists():
            raise FileExistsError("Please check your checkpoint file wether in the ~/.scDeconv folder")
        return cls(model=cls._model_cls.load_from_checkpoint(ckpt_path, map_location=map_location), device=device)
    
    @property
    def cell_types(self) -> np.ndarray:
        return self.reference.index.to_numpy()
    
    @property
    def top_genes(self) -> np.ndarray:
        return self.reference.columns.to_numpy()
    
    def predict(self, bulk: pd.DataFrame, batch_size: int | None = None):
        bulk_dataset = self._prepare_dataset(bulk)
        bulk_dataloader = DataLoader(bulk_dataset, batch_size=len(bulk_dataset) if batch_size is None else batch_size, shuffle=False)
        results = self.trainer.predict(model=self.model, dataloaders=bulk_dataloader)
        
        # results = torch.stack(results)
        proportion_results = torch.concat([res["prop"] for res in results])
        expression_results = torch.concat([res["expr"] for res in results])
        
        # for result in results:
        # predict_proportion = pd.DataFrame(results["prop"].cpu().numpy(), columns=self.cell_types, index=bulk.index)
        predict_proportion = pd.DataFrame(proportion_results.cpu().numpy(), columns=self.cell_types, index=bulk.index)
        
        predict_expression = list(map(
            lambda x: pd.DataFrame(x.cpu().numpy(), index=self.cell_types, columns=self.top_genes).apply(np.expm1), 
            # results["expr"]
            expression_results
        ))
        
        return predict_proportion, predict_expression
        
    def _prepare_dataset(self, bulk: pd.DataFrame):
        _bulk = bulk.copy(deep=True)
        _bulk = self._align_genes(_bulk, self.top_genes)
        _bulk = minmax_scale(_bulk, axis=1)
        return Bulkdataset(_bulk)
        
    @staticmethod
    def _align_genes(bulk: pd.DataFrame, top_genes: np.ndarray):
        genes = bulk.columns
        top_genes = pd.Index(top_genes)
        missing_genes = top_genes.difference(genes)
        print(f"Missing {len(missing_genes)} genes")
        missing_genes_df = pd.DataFrame(0.0, index=bulk.index, columns=missing_genes)
        bulk = pd.concat([bulk, missing_genes_df], axis=1)
        bulk = bulk[top_genes]
        return bulk
    


class Bulkdataset(Dataset):
    def __init__(self, bulk: np.ndarray) -> None:
        super().__init__()
        self.bulk = torch.from_numpy(bulk).float()
        
    def __len__(self) -> int:
        return self.bulk.shape[0]
    
    def __getitem__(self, index) -> torch.Tensor:
        return self.bulk[index]