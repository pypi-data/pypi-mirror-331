import gc
from pathlib import Path
from typing import Literal

import anndata as ad
import torch
from torch.utils.data import ConcatDataset, Dataset


class Anndataset(Dataset):
    def __init__(
        self, 
        adata: ad.AnnData, 
        n_top_genes: int,
        stage: Literal["fit", "test", "predict"] = "fit",
        # missing_genes: torch.Tensor | None = None
    ) -> None:
        super().__init__()
        assert stage in ["fit", "test", "predict"]
    
        self.stage = stage
            
        if stage in ["fit", "test"]:
            # self.bulk = torch.from_numpy(adata.to_df(layer=layer).to_numpy()).float()
            # self.prop = torch.from_numpy(adata.obsm["prop"].to_numpy()).float()
            # self.expr = torch.from_numpy(adata.uns["expr"]).float()
            self.bulk = torch.from_numpy(adata.obsm[f"X_{n_top_genes}_MMS"]).half()
            self.prop = torch.from_numpy(adata.obsm["prop"].to_numpy()).half()
            self.expr = torch.from_numpy(adata.uns[f"expr_{n_top_genes}_log1p"]).half()
            assert self.bulk.shape[0] == self.prop.shape[0] == self.expr.shape[0]
        elif stage == "predict":
            self.bulk = torch.from_numpy(adata.obsm[f"X_{n_top_genes}_MMS"]).half()
            
        # self.missing_genes = missing_genes if missing_genes else torch.zeros(n_top_genes, dtype=torch.bool)
    
    def __len__(self) -> int:
        return self.bulk.shape[0]

    def __getitem__(self, index) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor] | torch.Tensor:
        if self.stage in ["fit", "test"]:
            return self.bulk[index], self.prop[index], self.expr[index] # self.missing_genes
        elif self.stage == "predict":
            return self.bulk[index]
    
    @classmethod
    def from_file(
        cls,
        file: str | Path,
        n_top_genes: int,
        stage: Literal["fit", "test", "predict"] = "fit",
    ):
        adata = ad.read_h5ad(file)
        obj = cls(adata, n_top_genes, stage)
        del adata
        gc.collect()
        return obj
        
def load_dataset_from_anndata(
    adata_list: list[ad.AnnData], 
    n_top_genes: int,
    stage: Literal["fit", "test", "predict"] = "fit",
    # missing_genes: torch.Tensor | None = None
) -> Anndataset:
    return ConcatDataset([Anndataset(adata=adata, n_top_genes=n_top_genes, stage=stage) for adata in adata_list])

def load_dataset_from_files(
    folder: str | Path, 
    file_name_list: list[str], 
    n_top_genes: int,
    stage: Literal["fit", "test", "predict"] = "fit"
) -> Anndataset:
    if isinstance(folder, str):
        folder = Path(folder)
    for file_name in file_name_list:
        file_path = folder.joinpath(file_name)
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} not found")
    
    return ConcatDataset([Anndataset.from_file(file=folder.joinpath(file_name), n_top_genes=n_top_genes, stage=stage) for file_name in file_name_list])