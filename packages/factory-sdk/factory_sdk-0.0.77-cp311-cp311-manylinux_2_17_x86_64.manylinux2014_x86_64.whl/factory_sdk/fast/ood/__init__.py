import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from pydantic import BaseModel, Field
from sklearn.preprocessing import normalize
from sklearn.manifold import TSNE  # Import TSNE instead of UMAP
from factory_sdk.fast.algorithms.mmd import mmd_test_with_effect_size


class ShiftResult(BaseModel):
    p_value: float = Field(description="Statistical significance from MMD test")
    effect_size: float = Field(description="Magnitude of shift (MMD effect size)")
    train_outlier_rate: float = Field(
        description="Outlier fraction in the training data"
    )
    test_outlier_rate: float = Field(description="Outlier fraction in the test data")
    n_train_samples: int = Field(description="Number of training samples")
    n_test_samples: int = Field(description="Number of test samples")


class OODPipeline:
    def __init__(self, X_train: np.ndarray):
        """
        Initialize the OOD pipeline with training data.
        This sets up an IsolationForest to determine the outlier rate in training.
        """
        # 1. L2-normalize your training data so the pipeline consistently treats
        #    embedding direction as the main factor.
        X_train = normalize(X_train, axis=1, norm="l2")
        self.train = X_train

        # 2. Fit Isolation Forest on the L2-normalized training data
        self.isolation_forest = IsolationForest(
            n_estimators=100, contamination=0.1, random_state=42
        )
        self.isolation_forest.fit(self.train)

        # 3. Outliers in the training data
        train_preds = self.isolation_forest.predict(self.train)
        self.n_train_outliers = np.sum(train_preds == -1)
        self.n_train_samples = len(self.train)
        self.train_outlier_rate = self.n_train_outliers / self.n_train_samples

    def detect_shift(self, X: np.ndarray) -> ShiftResult:
        """
        Detect distribution shift between training data (self.train) and new data X:
          1. Perform MMD test (effect_size, p_value).
          2. Determine fraction of outliers in X via Isolation Forest.
          3. Return ShiftResult.
        """
        # 1. L2-normalize X before applying MMD test + Isolation Forest
        X = normalize(X, axis=1, norm="l2")

        # 2. MMD test with cosine kernel
        effect_size, p_value = mmd_test_with_effect_size(
            self.train,
            X,
            kernel="cosine",
            n_permutations=1000,  # Increase for more precise p-value
            random_state=42,
            dtype=np.float32,
            subsample=5000,
        )

        # 3. Outlier detection on test set
        test_preds = self.isolation_forest.predict(X)
        n_test_outliers = np.sum(test_preds == -1)
        n_test_samples = len(X)
        test_outlier_rate = n_test_outliers / n_test_samples

        # 4. Assemble the result
        return ShiftResult(
            p_value=p_value,
            effect_size=effect_size,
            train_outlier_rate=self.train_outlier_rate,
            test_outlier_rate=test_outlier_rate,
            n_train_samples=self.n_train_samples,
            n_test_samples=n_test_samples,
        )

    @classmethod
    def compute_2d(cls, train_embeddings, test_embeddings):
        """
        Project embeddings to 2D using t-SNE with a fixed random state.
        Vectors are assumed to be cosine distance embeddings so we use the 'cosine' metric.
        Note: t-SNE does not support out-of-sample transform; thus, we fit t-SNE on the combined data.
        """
        result = {"train": {}, "test": {}}

        # --- TEXT EMBEDDINGS ---
        if train_embeddings["text"] is not None and test_embeddings["text"] is not None:
            # (Optional) L2-normalize prior to t-SNE if you want purely angular geometry
            train_text_norm = normalize(train_embeddings["text"], axis=1, norm="l2")
            test_text_norm = normalize(test_embeddings["text"], axis=1, norm="l2")

            # Combine the normalized embeddings and run t-SNE
            combined_text = np.concatenate([train_text_norm, test_text_norm], axis=0)
            tsne_text = TSNE(n_components=2, metric="cosine", random_state=42)
            combined_text_2d = tsne_text.fit_transform(combined_text)

            # Split the result back into train and test parts
            n_train = train_text_norm.shape[0]
            result["train"]["text"] = combined_text_2d[:n_train]
            result["test"]["text"] = combined_text_2d[n_train:]
        else:
            result["train"]["text"] = None
            result["test"]["text"] = None

        # --- IMAGE EMBEDDINGS ---
        if (
            train_embeddings["image"] is not None
            and test_embeddings["image"] is not None
        ):
            # (Optional) L2-normalize prior to t-SNE
            train_image_norm = normalize(train_embeddings["image"], axis=1, norm="l2")
            test_image_norm = normalize(test_embeddings["image"], axis=1, norm="l2")

            # Combine the normalized embeddings and run t-SNE
            combined_image = np.concatenate([train_image_norm, test_image_norm], axis=0)
            tsne_image = TSNE(n_components=2, metric="cosine", random_state=42)
            combined_image_2d = tsne_image.fit_transform(combined_image)

            # Split the result back into train and test parts
            n_train = train_image_norm.shape[0]
            result["train"]["image"] = combined_image_2d[:n_train]
            result["test"]["image"] = combined_image_2d[n_train:]
        else:
            result["train"]["image"] = None
            result["test"]["image"] = None

        return result
