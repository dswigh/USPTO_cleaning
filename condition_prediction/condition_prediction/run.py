import dataclasses
import datetime
import json
import logging
import os
import pathlib
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import click

LOG = logging.getLogger(__name__)

import numpy as np
import pandas as pd
import tensorflow as tf
from click_loglevel import LogLevel
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from wandb.keras import WandbMetricsLogger, WandbModelCheckpoint

import wandb
from condition_prediction.constants import HARD_SELECTION, SOFT_SELECTION, TEACHER_FORCE
from condition_prediction.data_generator import get_datasets, unbatch_dataset
from condition_prediction.model import (
    build_teacher_forcing_model,
    update_teacher_forcing_model_weights,
)
from condition_prediction.utils import (
    TrainingMetrics,
    frequency_informed_accuracy,
    get_grouped_scores,
    get_random_splits,
    post_training_plots,
)

physical_devices = tf.config.experimental.list_physical_devices("GPU")
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


@dataclasses.dataclass(kw_only=True)
class ConditionPrediction:
    """
    Class for training a condition prediction model.

    1) Get the data ready for modelling
    1.1) Inputs: concat([rxn_diff_fp, product_fp])
    1.2) Targets: OHE

    """

    train_data_path: pathlib.Path
    test_data_path: pathlib.Path
    train_fp_path: pathlib.Path
    test_fp_path: pathlib.Path
    output_folder_path: pathlib.Path
    train_fraction: float
    train_val_split: float
    epochs: int
    generate_fingerprints: bool
    fp_size: int
    dropout: float
    hidden_size_1: int
    hidden_size_2: int
    lr: float
    reduce_lr_on_plateau_patience: int
    reduce_lr_on_plateau_factor: float
    batch_size: int
    workers: int
    shuffle_buffer_size: int
    prefetch_buffer_size: int
    interleave: bool
    evaluate_on_test_data: bool
    cache_train_data: bool = False
    cache_val_data: bool = False
    cache_test_data: bool = False
    early_stopping_patience: int
    eager_mode: bool
    wandb_logging: bool
    wandb_project: str
    wandb_entity: Optional[str] = None
    wandb_tags: Optional[List[str]] = None
    wandb_group: Optional[str] = None
    verbosity: int = 2

    def __post_init__(self) -> None:
        pass

    def run_model_arguments(self) -> None:
        train_df = pd.read_parquet(self.train_data_path)
        test_df = pd.read_parquet(self.test_data_path)
        train_fp = None
        test_fp = None
        if not self.generate_fingerprints:
            train_fp = np.load(self.train_fp_path)
            test_fp = np.load(self.test_fp_path)
        unnecessary_columns = [
            "date_of_experiment",
            "extracted_from_file",
            "grant_date",
            "is_mapped",
            "procedure_details",
            "rxn_str",
            "rxn_time",
            "temperature",
            "yield_000",
        ]
        train_df.drop(columns=unnecessary_columns, inplace=True)
        test_df.drop(columns=unnecessary_columns, inplace=True)
        self.run_model(
            train_val_df=train_df,
            test_df=test_df,
            train_val_fp=train_fp,
            test_fp=test_fp,
            output_folder_path=self.output_folder_path,
            train_fraction=self.train_fraction,
            train_val_split=self.train_val_split,
            epochs=self.epochs,
            fp_size=self.fp_size,
            dropout=self.dropout,
            hidden_size_1=self.hidden_size_1,
            hidden_size_2=self.hidden_size_2,
            lr=self.lr,
            reduce_lr_on_plateau_patience=self.reduce_lr_on_plateau_patience,
            reduce_lr_on_plateau_factor=self.reduce_lr_on_plateau_factor,
            batch_size=self.batch_size,
            workers=self.workers,
            eager_mode=self.eager_mode,
            cache_train_data=self.cache_train_data,
            cache_val_data=self.cache_val_data,
            cache_test_data=self.cache_test_data,
            shuffle_buffer_size=self.shuffle_buffer_size,
            prefetch_buffer_size=self.prefetch_buffer_size,
            interleave=self.interleave,
            early_stopping_patience=self.early_stopping_patience,
            evaluate_on_test_data=self.evaluate_on_test_data,
            wandb_project=self.wandb_project,
            wandb_entity=self.wandb_entity,
            wandb_logging=self.wandb_logging,
            wandb_tags=self.wandb_tags,
            wandb_group=self.wandb_group,
            verbosity=self.verbosity,
        )

    @staticmethod
    def get_frequency_informed_guess(
        train_val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        molecule_columns: List[str],
    ) -> Dict[str, Any]:
        mol_1_col = molecule_columns[0]
        mol_2_col = molecule_columns[1]
        mol_3_col = molecule_columns[2]
        mol_4_col = molecule_columns[3]
        mol_5_col = molecule_columns[4]

        # Evaulate whether the correct set of labels have been predicted, rather than treating them separately
        solvent_accuracy, most_common_solvents = frequency_informed_accuracy(
            (train_val_df[mol_1_col], train_val_df[mol_2_col]),
            (test_df[mol_1_col], test_df[mol_2_col]),
        )
        agent_accuracy, most_common_agents = frequency_informed_accuracy(
            (
                train_val_df[mol_3_col],
                train_val_df[mol_4_col],
                train_val_df[mol_5_col],
            ),
            (test_df[mol_3_col], test_df[mol_4_col], test_df[mol_5_col]),
        )
        overall_accuracy, most_common_combination = frequency_informed_accuracy(
            (
                train_val_df[mol_1_col],
                train_val_df[mol_2_col],
                train_val_df[mol_3_col],
                train_val_df[mol_4_col],
                train_val_df[mol_5_col],
            ),
            (
                test_df[mol_1_col],
                test_df[mol_2_col],
                test_df[mol_3_col],
                test_df[mol_4_col],
                test_df[mol_5_col],
            ),
        )

        # Save the naive_top_3 benchmark to json
        benchmark_dict = {
            f"most_common_solvents": most_common_solvents,
            f"most_common_agents": most_common_agents,
            f"most_common_combination": most_common_combination,
            f"frequency_informed_solvent_accuracy": solvent_accuracy,
            f"frequency_informed_agent_accuracy": agent_accuracy,
            f"frequency_informed_overall_accuracy": overall_accuracy,
        }

        return benchmark_dict

    @staticmethod
    def run_model(
        train_val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        output_folder_path,
        train_val_fp: Optional[np.ndarray] = None,
        test_fp: Optional[np.ndarray] = None,
        train_fraction: float = 1.0,
        train_val_split: float = 0.8,
        epochs: int = 20,
        early_stopping_patience: int = 5,
        evaluate_on_test_data: bool = False,
        train_mode: int = HARD_SELECTION,
        batch_size: int = 512,
        fp_size: int = 2048,
        dropout: float = 0.2,
        hidden_size_1: int = 1024,
        hidden_size_2: int = 100,
        lr: float = 0.01,
        reduce_lr_on_plateau_patience: int = 0,
        reduce_lr_on_plateau_factor: float = 0.1,
        workers: int = 1,
        shuffle_buffer_size: int = 1000,
        prefetch_buffer_size: Optional[int] = None,
        interleave: bool = False,
        cache_train_data: bool = False,
        cache_val_data: bool = False,
        cache_test_data: bool = False,
        eager_mode: bool = False,
        wandb_logging: bool = True,
        wandb_project: str = "orderly",
        wandb_entity: Optional[str] = None,
        wandb_tags: Optional[List[str]] = None,
        wandb_group: Optional[str] = None,
        verbosity: int = 2,
    ) -> None:
        """
        Run condition prediction training

        """
        config = locals()
        config.pop("train_val_df")
        config.pop("test_df")
        config.pop("train_val_fp")
        config.pop("test_fp")

        ### Data setup ###
        assert train_val_df.shape[1] == test_df.shape[1]

        # Concat train and test df
        df = pd.concat([train_val_df, test_df], axis=0)
        df = df.reset_index(drop=True)
        test_idx = np.arange(train_val_df.shape[0], df.shape[0])

        # Get indices for train and val
        train_idx, val_idx = get_random_splits(
            n_indices=train_val_df.shape[0],
            train_fraction=train_fraction,
            train_val_split=train_val_split,
        )

        # Apply these to the fingerprints
        if train_val_fp is not None:
            assert train_val_fp.shape[0] == train_val_df.shape[0]
            fp_size = train_val_fp.shape[1] // 2
            config.update({"fp_size": fp_size})
        if test_fp is not None:
            assert test_fp.shape[0] == test_df.shape[0]

        # If catalyst_000 exists, this means we had trust_labelling = True,
        # and we need to recast the columns to standardise the data
        if "catalyst_000" in df.columns:  # trust_labelling = True
            trust_labelling = True
            mol_1_col = "solvent_000"
            mol_2_col = "solvent_001"
            mol_3_col = "catalyst_000"
            mol_4_col = "reagent_000"
            mol_5_col = "reagent_001"

        else:  # trust_labelling = False
            trust_labelling = False
            mol_1_col = "solvent_000"
            mol_2_col = "solvent_001"
            mol_3_col = "agent_000"
            mol_4_col = "agent_001"
            mol_5_col = "agent_002"
        molecule_columns = [mol_1_col, mol_2_col, mol_3_col, mol_4_col, mol_5_col]

        (
            train_dataset,
            val_dataset,
            test_dataset,
            encoders,
        ) = get_datasets(
            df=df,
            train_idx=train_idx,
            val_idx=val_idx,
            test_idx=test_idx,
            fp_size=fp_size,
            train_val_fp=train_val_fp,
            test_fp=test_fp,
            train_mode=train_mode,
            molecule_columns=molecule_columns,
            batch_size=batch_size,
            shuffle_buffer_size=shuffle_buffer_size,
            prefetch_buffer_size=prefetch_buffer_size,
            interleave=interleave,
            cache_train_data=cache_train_data,
            cache_val_data=cache_val_data,
            cache_test_data=cache_test_data,
        )

        if evaluate_on_test_data:
            benchmark_dict = ConditionPrediction.get_frequency_informed_guess(
                train_val_df=train_val_df,
                test_df=test_df,
                molecule_columns=molecule_columns,
            )
            benchmark_file_path = output_folder_path / "freq_informed_acc.json"
            with open(benchmark_file_path, "w") as file:
                json.dump(benchmark_dict, file)

        del train_val_df
        del test_df
        LOG.info("Data ready for modelling")
        ### Model Setup ###
        model = build_teacher_forcing_model(
            pfp_len=fp_size,
            rxnfp_len=fp_size,
            mol1_dim=len(encoders[0].categories_[0]),
            mol2_dim=len(encoders[1].categories_[0]),
            mol3_dim=len(encoders[2].categories_[0]),
            mol4_dim=len(encoders[3].categories_[0]),
            mol5_dim=len(encoders[4].categories_[0]),
            N_h1=hidden_size_1,
            N_h2=hidden_size_2,
            l2v=0,  # TODO check what coef they used
            mode=train_mode,
            dropout_prob=dropout,
            use_batchnorm=True,
        )
        # we use a separate model for prediction because we use a recurrent setup for prediction
        # the pred model is only different after the first component (mol1)
        pred_model = build_teacher_forcing_model(
            pfp_len=fp_size,
            rxnfp_len=fp_size,
            mol1_dim=len(encoders[0].categories_[0]),
            mol2_dim=len(encoders[1].categories_[0]),
            mol3_dim=len(encoders[2].categories_[0]),
            mol4_dim=len(encoders[3].categories_[0]),
            mol5_dim=len(encoders[4].categories_[0]),
            N_h1=hidden_size_1,
            N_h2=hidden_size_2,
            l2v=0,
            mode=HARD_SELECTION,
            dropout_prob=dropout,
            use_batchnorm=True,
        )

        model.compile(
            loss=[
                tf.keras.losses.CategoricalCrossentropy(from_logits=False)
                for _ in range(5)
            ],
            loss_weights=[1, 1, 1, 1, 1],
            optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
            metrics={
                f"mol{i}": [
                    "acc",
                    tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top3"),
                    tf.keras.metrics.TopKCategoricalAccuracy(k=5, name="top5"),
                ]
                for i in range(1, 6)
            },
            run_eagerly=eager_mode,
        )
        update_teacher_forcing_model_weights(
            update_model=pred_model, to_copy_model=model
        )

        ### Training ###
        # callbacks = [
        #     tf.keras.callbacks.TensorBoard(
        #         log_dir=log_dir(prefix="TF_", comment="_MOREDATA_REG_HARDSELECT")
        #     )
        # ]
        callbacks = [
            TrainingMetrics(
                n_train=train_idx.shape[0],
                batch_size=batch_size,
            )
        ]
        # Define the EarlyStopping callback
        if early_stopping_patience != 0:
            early_stop = EarlyStopping(
                monitor="val_loss", patience=early_stopping_patience
            )
            callbacks.append(early_stop)
        if reduce_lr_on_plateau_patience != 0:
            reduce_lr = ReduceLROnPlateau(
                monitor="val_loss",
                factor=reduce_lr_on_plateau_factor,
                patience=reduce_lr_on_plateau_patience,
                min_lr=1e-6,
            )
            callbacks.append(reduce_lr)
        checkpoint_filepath = "models/{epoch:02d}"
        if wandb_logging:
            wandb_tags = [] if wandb_tags is None else wandb_tags
            if "Condition Prediction" not in wandb_tags:
                wandb_tags.append("Condition Prediction")
            wandb_run = wandb.init(  # type: ignore
                project=wandb_project,
                entity=wandb_entity,
                tags=wandb_tags,
                group=wandb_group,
                config=config,
            )
            callbacks.extend(
                [
                    WandbMetricsLogger(),
                    WandbModelCheckpoint(checkpoint_filepath, save_best_only=True),
                ]
            )
        else:
            callbacks.append(
                ModelCheckpoint(
                    filepath=checkpoint_filepath,
                    save_best_only=True,
                )
            )

        use_multiprocessing = True if workers > 0 else False
        h = model.fit(
            train_dataset,
            epochs=epochs,
            verbose=verbosity,
            validation_data=val_dataset,
            callbacks=callbacks,
            use_multiprocessing=use_multiprocessing,
            workers=workers,
        )
        # Load the best model back
        model.load_weights(checkpoint_filepath)
        update_teacher_forcing_model_weights(
            update_model=pred_model, to_copy_model=model
        )

        # Save the train and val metrics
        train_val_file_path = output_folder_path / "train_val_metrics.json"
        train_val_metrics_dict = h.history
        train_val_metrics_dict["trust_labelling"] = trust_labelling
        with open(train_val_file_path, "w") as file:
            json.dump(train_val_metrics_dict, file)

        ### Evaluation ####
        post_training_plots(
            h, output_folder_path=output_folder_path, molecule_columns=molecule_columns
        )

        # Save the final performance on the test set
        del train_dataset
        _, y_test_data = unbatch_dataset(test_dataset)
        if evaluate_on_test_data:
            # Evaluate the model on the test set
            test_metrics = model.evaluate(
                test_dataset,
                use_multiprocessing=use_multiprocessing,
                workers=workers,
            )
            test_metrics_dict = dict(zip(model.metrics_names, test_metrics))
            test_metrics_dict["trust_labelling"] = trust_labelling

            ### Grouped scores
            predictions = model.predict(
                test_dataset,
                use_multiprocessing=use_multiprocessing,
                workers=workers,
            )

            # Solvent scores
            solvent_scores = get_grouped_scores(
                y_test_data[:2], predictions[:2], encoders[:2]
            )
            test_metrics_dict["test_solvent_accuracy"] = np.mean(solvent_scores)

            # 3 agents scores
            agent_scores = get_grouped_scores(
                y_test_data[2:], predictions[2:], encoders[2:]
            )
            test_metrics_dict["test_three_agents_accuracy"] = np.mean(agent_scores)

            # Overall scores
            overall_scores = np.stack([solvent_scores, agent_scores], axis=1).all(
                axis=1
            )
            test_metrics_dict["test_overall_accuracy"] = np.mean(overall_scores)

            # Save the test metrics
            test_metrics_file_path = output_folder_path / "test_metrics.json"
            # Save the dictionary as a JSON file
            with open(test_metrics_file_path, "w") as file:
                json.dump(test_metrics_dict, file)

            if wandb_logging:
                # Log artifact
                artifact = wandb.Artifact(  # type: ignore
                    name="test_metrics",
                    type="metrics",
                    description="Metrics on the test set",
                )
                artifact.add_dir(output_folder_path)
                wandb_run.log_artifact(artifact)  # type: ignore
                # Add  run summary
                wandb_run.summary.update(benchmark_dict)  # type: ignore
                wandb_run.summary.update(test_metrics_dict)  # type: ignore


@click.command()
@click.option(
    "--train_data_path",
    type=str,
    default="/data/orderly/datasets/orderly_no_trust_with_map_train.parquet",
    show_default=True,
    help="The filepath where the training data is found",
)
@click.option(
    "--test_data_path",
    default="no_trust_with_map_model",
    type=str,
    help="The filepath where the test data is found",
)
@click.option(
    "--output_folder_path",
    default="/data/orderly/datasets/orderly_no_trust_with_map_train.parquet",
    type=str,
    help="The filepath where the test data is found",
)
@click.option(
    "--train_fraction",
    default=1.0,
    type=float,
    help="The fraction of the train data that will actually be used for training (ignore the rest)",
)
@click.option(
    "--train_val_split",
    default=0.8,
    type=float,
    help="The fraction of the train data that is used for training (the rest is used for validation)",
)
@click.option(
    "--epochs",
    default=20,
    type=int,
    help="The number of epochs used for training",
)
@click.option(
    "--early_stopping_patience",
    default=5,
    type=int,
    help="Number of epochs with no improvement after which training will be stopped. If 0, then early stopping is disabled.",
)
@click.option(
    "--evaluate_on_test_data",
    default=False,
    type=bool,
    help="If True, will evaluate the model on the test data",
)
@click.option(
    "--generate_fingerprints",
    default=False,
    type=bool,
    show_default=True,
    help="If True, will generate fingerprints on the fly instead of loading them from memory",
)
@click.option(
    "--workers",
    default=0,
    type=int,
    help="The number of workers to use for generating fingerprints. Defaults to 75\% of the CPUs on the machine. Defaults to 0",
)
@click.option(
    "--fp_size",
    default=2048,
    type=int,
    help="The size of the fingerprint used in fingerprint generation",
)
@click.option(
    "--dropout",
    default=0.2,
    type=float,
    help="The dropout rate used in the model",
)
@click.option(
    "--hidden_size_1",
    default=1024,
    type=int,
    help="The size of the first hidden layer in the model",
)
@click.option(
    "--hidden_size_2",
    default=100,
    type=int,
    help="The size of the second hidden layer in the model",
)
@click.option(
    "--lr",
    default=0.01,
    type=float,
    help="The learning rate used in the model",
)
@click.option(
    "--reduce_lr_on_plateau_patience",
    default=0,
    type=int,
    help="Number of epochs with no improvement after which learning rate will be reduced. If 0, then learning rate reduction is disabled.",
)
@click.option(
    "--reduce_lr_on_plateau_factor",
    default=0.1,
    type=float,
    help="Factor by which the learning rate will be reduced. new_lr = lr * factor",
)
@click.option(
    "--batch_size",
    default=512,
    type=int,
    help="The batch size used during training of the model",
)
@click.option(
    "--wandb_logging",
    default=True,
    type=bool,
    help="If True, will log to wandb",
)
@click.option(
    "--wandb_entity",
    default=None,
    type=str,
    help="The entity to use for logging to wandb",
)
@click.option(
    "--wandb_project",
    default="orderly",
    type=str,
    help="The project to use for logging to wandb",
)
@click.option(
    "--wandb_tag", multiple=True, default=None, help="Tags for weights and biases run"
)
@click.option(
    "--wandb_group",
    default=None,
    type=str,
    help="The group to use for logging to wandb",
)
@click.option(
    "--eager_mode",
    is_flag=True,
    default=False,
)
@click.option(
    "--cache_train_data",
    default=False,
    type=bool,
    help="If True, will cache the training data",
)
@click.option(
    "--cache_val_data",
    default=False,
    type=bool,
    help="If True, will cache the validation data",
)
@click.option(
    "--cache_test_data",
    default=False,
    type=bool,
    help="If True, will cache the test data",
)
@click.option(
    "--shuffle_buffer_size",
    default=1000,
    type=int,
    help="The buffer size used for shuffling the data",
)
@click.option(
    "--prefetch_buffer_size",
    default=None,
    type=int,
    help="The buffer size used for prefetching the data. Defaults to 5x the batch size",
)
@click.option(
    "--interleave",
    default=False,
    type=bool,
    help="If True, will interleave the data processing",
)
@click.option(
    "--overwrite",
    type=bool,
    default=False,
    show_default=True,
    help="If true, will overwrite the contents in the output folder, else will through an error if the folder is not empty",
)
@click.option(
    "--verbosity",
    type=int,
    default=2,
    show_default=True,
    help="The verbosity level of the logger. 0 is silent, 1 is progress bar, 2 is one line per epoch",
)
@click.option(
    "--log_file",
    type=str,
    default="default_path_model.log",
    show_default=True,
    help="path for the log file for model",
)
@click.option("--log-level", type=LogLevel(), default=logging.INFO)
def main_click(
    train_data_path: pathlib.Path,
    test_data_path: pathlib.Path,
    output_folder_path: pathlib.Path,
    train_fraction: float,
    train_val_split: float,
    epochs: int,
    early_stopping_patience: int,
    evaluate_on_test_data: bool,
    generate_fingerprints: bool,
    workers: int,
    fp_size: int,
    dropout: float,
    hidden_size_1: int,
    hidden_size_2: int,
    lr: float,
    reduce_lr_on_plateau_patience: int,
    reduce_lr_on_plateau_factor: float,
    batch_size: int,
    wandb_logging: bool,
    wandb_project: str,
    wandb_entity: Optional[str],
    wandb_tag: List[str],
    wandb_group: Optional[str],
    overwrite: bool,
    eager_mode: bool,
    cache_train_data: bool,
    cache_val_data: bool,
    cache_test_data: bool,
    shuffle_buffer_size: int,
    prefetch_buffer_size: int,
    interleave: bool,
    log_file: pathlib.Path = pathlib.Path("model.log"),
    log_level: int = logging.INFO,
    verbosity: int = 2,
) -> None:
    """
    After extraction and cleaning of ORD data, this will train a condition prediction model.


    Functionality:
    1) Load the the train and test data
    2) Get the fingerprint to use as input (Morgan fp from rdkit). Generating FP is slow, so we do it once and save it.
    3) Apply OHE to the target variables
    3) Train the model (use tqdm to show progress)
        3.1) Save graphs of training & validation loss and accuracy
        3.2) Save the model
    4) Evaluate the model on the test data
        4.1) Save the test loss and accuracy in a log file

    We can then use the model to predict the condition of a reaction.

    """
    wandb_tags = wandb_tag
    main(
        train_data_path=train_data_path,
        test_data_path=test_data_path,
        output_folder_path=output_folder_path,
        train_fraction=train_fraction,
        train_val_split=train_val_split,
        epochs=epochs,
        early_stopping_patience=early_stopping_patience,
        evaluate_on_test_data=evaluate_on_test_data,
        generate_fingerprints=generate_fingerprints,
        workers=workers,
        fp_size=fp_size,
        dropout=dropout,
        hidden_size_1=hidden_size_1,
        hidden_size_2=hidden_size_2,
        lr=lr,
        reduce_lr_on_plateau_patience=reduce_lr_on_plateau_patience,
        reduce_lr_on_plateau_factor=reduce_lr_on_plateau_factor,
        cache_train_data=cache_train_data,
        cache_val_data=cache_val_data,
        cache_test_data=cache_test_data,
        batch_size=batch_size,
        wandb_logging=wandb_logging,
        wandb_project=wandb_project,
        wandb_entity=wandb_entity,
        wandb_tags=wandb_tags,
        wandb_group=wandb_group,
        overwrite=overwrite,
        eager_mode=eager_mode,
        shuffle_buffer_size=shuffle_buffer_size,
        prefetch_buffer_size=prefetch_buffer_size,
        interleave=interleave,
        log_file=log_file,
        log_level=log_level,
        verbosity=verbosity,
    )


def main(
    train_data_path: pathlib.Path,
    test_data_path: pathlib.Path,
    output_folder_path: pathlib.Path,
    train_fraction: float,
    train_val_split: float,
    epochs: int,
    early_stopping_patience: int,
    evaluate_on_test_data: bool,
    generate_fingerprints: bool,
    workers: int,
    fp_size: int,
    dropout: float,
    hidden_size_1: int,
    hidden_size_2: int,
    lr: float,
    reduce_lr_on_plateau_patience: int,
    reduce_lr_on_plateau_factor: float,
    batch_size: int,
    wandb_logging: bool,
    wandb_project: str,
    wandb_entity: Optional[str],
    wandb_tags: List[str],
    wandb_group: Optional[str],
    overwrite: bool,
    eager_mode: bool,
    cache_train_data: bool,
    cache_val_data: bool,
    cache_test_data: bool,
    shuffle_buffer_size: int,
    prefetch_buffer_size: int,
    interleave: bool,
    log_file: pathlib.Path = pathlib.Path("model.log"),
    log_level: int = logging.INFO,
    verbosity: int = 2,
) -> None:
    """
    After extraction and cleaning of ORD data, this will train a condition prediction model.


    Functionality:
    1) Load the the train and test data
    2) Get the fingerprint to use as input (Morgan fp from rdkit). Generating FP is slow, so we do it once and save it.
    3) Apply OHE to the target variables
    3) Train the model (use tqdm to show progress)
        3.1) Save graphs of training & validation loss and accuracy
        3.2) Save the model
    4) Evaluate the model on the test data
        4.1) Save the test loss and accuracy in a log file

    We can then use the model to predict the condition of a reaction.

    """
    train_data_path = pathlib.Path(train_data_path)
    test_data_path = pathlib.Path(test_data_path)
    output_folder_path = pathlib.Path(output_folder_path)

    log_file = pathlib.Path(output_folder_path) / f"model.log"
    if log_file != "default_path_model.log":
        log_file = pathlib.Path(log_file)

    start_time = datetime.datetime.now()

    output_folder_path.mkdir(parents=True, exist_ok=True)

    if not overwrite:
        # Assert that the output_folder_path is empty
        assert (
            len(list(output_folder_path.iterdir())) == 0
        ), f"{output_folder_path} is not empty"

    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        encoding="utf-8",
        format="%(name)s - %(levelname)s - %(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=log_level,
    )

    if not isinstance(train_data_path, pathlib.Path):
        e = ValueError(f"Expect pathlib.Path: got {type(train_data_path)}")
        LOG.error(e)
        raise e
    if not isinstance(test_data_path, pathlib.Path):
        e = ValueError(f"Expect pathlib.Path: got {type(test_data_path)}")
        LOG.error(e)
        raise e
    if not isinstance(output_folder_path, pathlib.Path):
        e = ValueError(f"Expect pathlib.Path: got {type(test_data_path)}")
        LOG.error(e)
        raise e

    fp_directory = train_data_path.parent / "fingerprints"
    fp_directory.mkdir(parents=True, exist_ok=True)
    # Define the train_fp_path
    train_fp_path = fp_directory / (train_data_path.stem + ".npy")
    test_fp_path = fp_directory / (test_data_path.stem + ".npy")

    LOG.info(f"Beginning model training, saving to {output_folder_path}")

    instance = ConditionPrediction(
        train_data_path=train_data_path,
        test_data_path=test_data_path,
        train_fp_path=train_fp_path,
        test_fp_path=test_fp_path,
        output_folder_path=output_folder_path,
        train_fraction=train_fraction,
        train_val_split=train_val_split,
        generate_fingerprints=generate_fingerprints,
        fp_size=fp_size,
        dropout=dropout,
        hidden_size_1=hidden_size_1,
        hidden_size_2=hidden_size_2,
        lr=lr,
        reduce_lr_on_plateau_patience=reduce_lr_on_plateau_patience,
        reduce_lr_on_plateau_factor=reduce_lr_on_plateau_factor,
        batch_size=batch_size,
        workers=workers,
        cache_train_data=cache_train_data,
        cache_val_data=cache_val_data,
        cache_test_data=cache_test_data,
        shuffle_buffer_size=shuffle_buffer_size,
        prefetch_buffer_size=prefetch_buffer_size,
        interleave=interleave,
        epochs=epochs,
        early_stopping_patience=early_stopping_patience,
        evaluate_on_test_data=evaluate_on_test_data,
        wandb_entity=wandb_entity,
        wandb_project=wandb_project,
        wandb_logging=wandb_logging,
        wandb_tags=list(wandb_tags),
        wandb_group=wandb_group,
        eager_mode=eager_mode,
        verbosity=verbosity,
    )

    instance.run_model_arguments()

    LOG.info(f"Completed model training, saving to {output_folder_path}")

    end_time = datetime.datetime.now()
    LOG.info("Training complete, duration: {}".format(end_time - start_time))
