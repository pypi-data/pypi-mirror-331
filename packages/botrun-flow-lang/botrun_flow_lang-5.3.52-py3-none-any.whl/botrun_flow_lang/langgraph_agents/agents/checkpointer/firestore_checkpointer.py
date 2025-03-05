from typing import Any, Dict, List, Optional, Tuple, AsyncIterator, Iterator, cast
import json
import time
import uuid
from datetime import datetime

from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from botrun_flow_lang.constants import CHECKPOINTER_STORE_NAME


class FirestoreCheckpointer(BaseCheckpointSaver):
    """Checkpointer implementation that uses Firestore for storage.

    This implementation provides both synchronous and asynchronous methods.
    """

    def __init__(
        self,
        env_name: str,
        serializer: Optional[SerializerProtocol] = None,
        collection_name: Optional[str] = None,
    ):
        """Initialize the Firestore checkpointer.

        Args:
            env_name: Environment name to be used as prefix for collection.
            serializer: Optional serializer to use for converting values to storable format.
            collection_name: Optional custom collection name. If not provided,
                             it will use {env_name}-{CHECKPOINTER_STORE_NAME}.
        """
        self.serializer = serializer or JsonPlusSerializer()
        self._collection_name = (
            collection_name or f"{env_name}-{CHECKPOINTER_STORE_NAME}"
        )
        self.db = firestore.Client()
        self.collection = self.db.collection(self._collection_name)

    def _get_checkpoint_id(self, config: Dict[str, Any]) -> str:
        """Get the checkpoint ID from config or generate a new one.

        Args:
            config: Configuration dict containing checkpoint identification.

        Returns:
            The checkpoint ID as a string.
        """
        configurable = config.get("configurable", {})
        checkpoint_id = configurable.get("checkpoint_id")
        if not checkpoint_id:
            checkpoint_id = str(uuid.uuid4())
            if "configurable" not in config:
                config["configurable"] = {}
            config["configurable"]["checkpoint_id"] = checkpoint_id
        return checkpoint_id

    def _get_thread_id(self, config: Dict[str, Any]) -> str:
        """Get the thread ID from config.

        Args:
            config: Configuration dict containing thread identification.

        Returns:
            The thread ID as a string.
        """
        configurable = config.get("configurable", {})
        thread_id = configurable.get("thread_id")
        if not thread_id:
            raise ValueError("Thread ID is required in the config")
        return thread_id

    def _get_checkpoint_doc_ref(self, thread_id: str, checkpoint_id: str):
        """Get the Firestore document reference for a checkpoint.

        Args:
            thread_id: The thread ID.
            checkpoint_id: The checkpoint ID.

        Returns:
            Firestore document reference.
        """
        return self.collection.document(f"{thread_id}_{checkpoint_id}")

    def _get_writes_doc_ref(self, thread_id: str, checkpoint_id: str, node_name: str):
        """Get the Firestore document reference for pending writes.

        Args:
            thread_id: The thread ID.
            checkpoint_id: The checkpoint ID.
            node_name: The node name.

        Returns:
            Firestore document reference.
        """
        return self.collection.document(
            f"{thread_id}_{checkpoint_id}_writes_{node_name}"
        )

    def put(
        self,
        config: Dict[str, Any],
        values: Dict[str, Any],
        next_: Tuple[str, ...],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Store a checkpoint with its configuration and metadata.

        Args:
            config: Configuration dict containing thread and checkpoint identification.
            values: Dict of values to store.
            next_: Tuple of next nodes to execute.
            metadata: Dict of metadata to store with the checkpoint.

        Returns:
            Updated config dict with checkpoint_id.
        """
        thread_id = self._get_thread_id(config)
        checkpoint_id = self._get_checkpoint_id(config)

        # Serialize values
        serialized_values = {k: self.serializer.serialize(v) for k, v in values.items()}

        # Create checkpoint document
        doc_ref = self._get_checkpoint_doc_ref(thread_id, checkpoint_id)

        timestamp = datetime.now().isoformat()

        doc_data = {
            "config": config,
            "values": serialized_values,
            "next": list(next_),  # Convert tuple to list for Firestore
            "metadata": metadata,
            "created_at": timestamp,
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
        }

        # Add parent config if in metadata
        if "parent_config" in metadata:
            doc_data["parent_config"] = metadata["parent_config"]

        try:
            doc_ref.set(doc_data)
        except GoogleCloudError as e:
            print(f"Error storing checkpoint {checkpoint_id}: {e}")
            raise

        return config

    def put_writes(
        self,
        config: Dict[str, Any],
        node_name: str,
        writes: Dict[str, Any],
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        Args:
            config: Configuration dict containing thread and checkpoint identification.
            node_name: Name of the node that produced the writes.
            writes: Dict of writes to store.
        """
        thread_id = self._get_thread_id(config)
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")

        if not checkpoint_id:
            raise ValueError("Checkpoint ID must be present in config")

        # Serialize writes
        serialized_writes = {k: self.serializer.serialize(v) for k, v in writes.items()}

        # Create writes document
        doc_ref = self._get_writes_doc_ref(thread_id, checkpoint_id, node_name)

        doc_data = {
            "writes": serialized_writes,
            "node_name": node_name,
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "created_at": datetime.now().isoformat(),
        }

        try:
            doc_ref.set(doc_data)
        except GoogleCloudError as e:
            print(
                f"Error storing writes for node {node_name} in checkpoint {checkpoint_id}: {e}"
            )
            raise

    def get_tuple(
        self,
        config: Dict[str, Any],
    ) -> Tuple[
        Dict[str, Any],
        Dict[str, Any],
        Tuple[str, ...],
        Dict[str, Any],
        Optional[Dict[str, Any]],
    ]:
        """Fetch a checkpoint tuple for a given configuration.

        Args:
            config: Configuration dict containing thread and checkpoint identification.

        Returns:
            Tuple of (config, values, next, metadata, parent_config).
        """
        thread_id = self._get_thread_id(config)
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")

        if not checkpoint_id:
            # Get the latest checkpoint for this thread
            query = (
                self.collection.where("thread_id", "==", thread_id)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(1)
            )
            docs = list(query.stream())

            if not docs:
                # No checkpoints found for this thread
                raise ValueError(f"No checkpoints found for thread {thread_id}")

            doc = docs[0]
        else:
            # Get the specific checkpoint
            doc_ref = self._get_checkpoint_doc_ref(thread_id, checkpoint_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise ValueError(
                    f"Checkpoint {checkpoint_id} not found for thread {thread_id}"
                )

        data = doc.to_dict()

        # Deserialize values
        values = {
            k: self.serializer.deserialize(v) for k, v in data.get("values", {}).items()
        }

        # Convert next from list back to tuple
        next_ = tuple(data.get("next", []))

        # Get parent config if it exists
        parent_config = data.get("parent_config")

        return (
            data.get("config", {}),
            values,
            next_,
            data.get("metadata", {}),
            parent_config,
        )

    def list(
        self,
        config: Dict[str, Any],
        **kwargs: Any,
    ) -> Iterator[
        Tuple[
            Dict[str, Any],
            Dict[str, Any],
            Tuple[str, ...],
            Dict[str, Any],
            Optional[Dict[str, Any]],
        ]
    ]:
        """List checkpoints that match a given configuration and filter criteria.

        Args:
            config: Configuration dict containing thread identification.
            **kwargs: Additional filter criteria.

        Returns:
            Iterator of checkpoint tuples.
        """
        thread_id = self._get_thread_id(config)

        # Build the query
        query = self.collection.where("thread_id", "==", thread_id)

        # Apply filter for checkpoint_id if provided
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")
        if checkpoint_id:
            query = query.where("checkpoint_id", "==", checkpoint_id)

        # Get all documents sorted by created_at in descending order
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

        # Apply limit if provided
        limit = kwargs.get("limit")
        if limit is not None:
            query = query.limit(limit)

        # Stream the results
        for doc in query.stream():
            data = doc.to_dict()

            # Skip documents that are not checkpoints (e.g., writes documents)
            if "values" not in data:
                continue

            # Deserialize values
            values = {
                k: self.serializer.deserialize(v)
                for k, v in data.get("values", {}).items()
            }

            # Convert next from list back to tuple
            next_ = tuple(data.get("next", []))

            # Get parent config if it exists
            parent_config = data.get("parent_config")

            yield (
                data.get("config", {}),
                values,
                next_,
                data.get("metadata", {}),
                parent_config,
            )

    # Async implementation

    async def aput(
        self,
        config: Dict[str, Any],
        values: Dict[str, Any],
        next_: Tuple[str, ...],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Async version: Store a checkpoint with its configuration and metadata."""
        # For Firestore, we can use the synchronous version as it's non-blocking
        return self.put(config, values, next_, metadata)

    async def aput_writes(
        self,
        config: Dict[str, Any],
        node_name: str,
        writes: Dict[str, Any],
    ) -> None:
        """Async version: Store intermediate writes linked to a checkpoint."""
        # For Firestore, we can use the synchronous version as it's non-blocking
        return self.put_writes(config, node_name, writes)

    async def aget_tuple(
        self,
        config: Dict[str, Any],
    ) -> Tuple[
        Dict[str, Any],
        Dict[str, Any],
        Tuple[str, ...],
        Dict[str, Any],
        Optional[Dict[str, Any]],
    ]:
        """Async version: Fetch a checkpoint tuple for a given configuration."""
        # For Firestore, we can use the synchronous version as it's non-blocking
        return self.get_tuple(config)

    async def alist(
        self,
        config: Dict[str, Any],
        **kwargs: Any,
    ) -> AsyncIterator[
        Tuple[
            Dict[str, Any],
            Dict[str, Any],
            Tuple[str, ...],
            Dict[str, Any],
            Optional[Dict[str, Any]],
        ]
    ]:
        """Async version: List checkpoints that match a given configuration and filter criteria."""
        # For Firestore, we convert the synchronous iterator to an async iterator
        for item in self.list(config, **kwargs):
            yield item
