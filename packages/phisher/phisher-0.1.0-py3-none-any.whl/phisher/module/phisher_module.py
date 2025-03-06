import torchmetrics
import torch
import torch.nn.functional as F
import pytorch_lightning as pl


class PhisherhModule(pl.LightningModule):
    def __init__(self, model, optimizer, learning_rate=1e-3):
        super().__init__()
        self.save_hyperparameters()
        self.learning_rate = learning_rate
        self.model = model
        self.optimizer = optimizer

        self.accuracy = torchmetrics.Accuracy(task="binary")
        self.f1 = torchmetrics.F1Score(task="binary")
        self.precision = torchmetrics.Precision(task="binary")
        self.recall = torchmetrics.Recall(task="binary")
        self.auroc = torchmetrics.classification.AUROC(task="binary")

    def forward(self, x):
        return self.model(x)

    def compute_loss(self, x, y):
        x = x.squeeze(dim=1) if x.ndim == 2 and x.shape[1] == 1 else x
        return F.binary_cross_entropy_with_logits(x, y.float())

    def common_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(x)
        loss = self.compute_loss(outputs, y)
        return loss, outputs, y

    def common_test_valid_step(self, batch, batch_idx):
        loss, outputs, y = self.common_step(batch, batch_idx)
        probs = torch.sigmoid(outputs.squeeze(1))
        preds = (probs >= 0.5).int()

        acc = self.accuracy(preds, y)
        f1 = self.f1(preds, y)
        precision = self.precision(preds, y)
        recall = self.recall(preds, y)
        auc = self.auroc(probs, y)
        return loss, acc, f1, precision, recall, auc

    def training_step(self, batch, batch_idx):
        loss, acc, _, __, ___, auc = self.common_test_valid_step(batch, batch_idx)
        self.log("train_loss", loss, on_step=True, on_epoch=True, logger=True)
        self.log("train_acc", acc, on_step=True, on_epoch=True, logger=True)
        self.log("train_auc", auc, on_step=True, on_epoch=False, logger=True)
        return loss

    def validation_step(self, batch, batch_idx):
        loss, acc, f1, precision, recall, auc = self.common_test_valid_step(
            batch, batch_idx
        )
        self.log("val_loss", loss)
        self.log("val_acc", acc)
        self.log("val_f1", f1)
        self.log("val_precision", precision)
        self.log("val_recall", recall)
        self.log("val_auc", auc)
        return loss

    def test_step(self, batch, batch_idx):
        loss, acc, f1, precision, recall, auc = self.common_test_valid_step(
            batch, batch_idx
        )
        self.log("test_loss", loss)
        self.log("test_acc", acc)
        self.log("test_f1", f1)
        self.log("test_precision", precision)
        self.log("test_recall", recall)
        self.log("test_auc", auc)
        return loss

    def configure_optimizers(self):
        return self.optimizer

    def log_metadata(self, dataset_name: str, model_name: str):
        self.logger.experiment.config.update(
            {
                "dataset_name": dataset_name,
                "model_name": model_name,
            }
        )
