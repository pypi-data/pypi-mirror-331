from dotenv import load_dotenv
import os
import time
from groclake.datalake import Datalake

load_dotenv()

class Config:
    # Redis Configuration
    REDIS_CONFIG = {
        "host": os.getenv("REDIS_HOST", "localhost"),  # Default to localhost if not set
        "port": int(os.getenv("REDIS_PORT", 6379)),  # Default to 6379 if not set
    }

class Memorylake(Datalake):
    def __init__(self):
        super().__init__()

        # Define the configuration for Redis connection
        REDIS_CONFIG = Config.REDIS_CONFIG
        REDIS_CONFIG['connection_type'] = 'redis'

        # Create and add Redis connection to the pipeline
        self.test_pipeline = self.create_pipeline(name="redis_pipeline")
        self.test_pipeline.add_connection(name="redis_connection", config=REDIS_CONFIG)

        # Execute all connections at once
        self.execute_all()

        # Initialize Redis connection
        self.connections = {
            "redis_connection": self.get_connection("redis_connection"),
        }

    def get_connection(self, connection_name):
        """
        Returns a connection by name from the pipeline.
        """
        return self.test_pipeline.get_connection_by_name(connection_name)

    @staticmethod
    def validate_memory_type(memory_type):
        """Ensure memory_type is either '0' or '1'."""
        if memory_type not in ['0', '1']:
            raise ValueError("Invalid memory_type. It must be '0' or '1'.")

    @staticmethod
    def generate_key(user_uuid, context_entity_id, context_id, memory_type, memory_id):
        """Generates a unique key by concatenating user_uuid, context_entity_id, context_id, memory_type, and memory_id."""
        Memorylake.validate_memory_type(memory_type)
        return f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:{memory_id}"

    def short_memory_create(self, user_uuid, memory_context, memory):
        """Creates a key-value pair in Redis only if the key does not already exist."""
        memory_type = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(memory_type)

        # Generate the key
        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            memory_type,
            memory_context['memory_id']
        )

        value = {
            "query_text": memory['query_text'],
            "response_text": memory['response_text'],
            "memory_metadata": [
                {
                    "time": memory['time'],
                    "memory_id": memory_context['memory_id'],
                    "context_id": memory_context['context_id'],
                }
            ],
            "intent": memory.get("intent", ""),
            "entities": memory.get("entities", []),
            "metadata": memory.get("metadata", []),
        }

        ttl = memory.get('cache_ttl', 3600)
        connection = self.connections.get("redis_connection")
        if not connection:
            raise ConnectionError("Redis connection is not available.")

        redis_client = connection.connection

        # Check if the key already exists in Redis
        if redis_client.exists(key):
            raise ValueError(f"Key '{key}' already exists. Cannot create a new value for the same key.")

        # Store the new key-value pair in Redis
        redis_client.set(key, str(value), ex=ttl)

        # Add the key to a sorted set with the current timestamp as the score
        sorted_set_key = f"{user_uuid}:{memory_context['context_id']}:{memory_context['context_entity_id']}:{memory_type}:messages"
        redis_client.zadd(sorted_set_key, {key: time.time()})

        return f"Key '{key}' created with value '{value}' and TTL {ttl}s."

    def short_memory_read(self, user_uuid, memory_context, n=None):
        """
        Reads a value from Redis or performs wildcard searches based on input parameters.
        If `n` is provided, fetches the latest `n` messages for the given context.
        If `n` is None, performs a wildcard search based on the provided memory_context.
        Supports fetching all `context_entity_id` values when not provided.
        """
        connection = self.connections.get("redis_connection")
        if not connection:
            raise ConnectionError("Redis connection is not available.")

        if n is not None:
            # Fetch the latest `n` messages
            context_id = memory_context.get('context_id', '*')
            context_entity_id = memory_context.get('context_entity_id', '*')
            memory_type = memory_context.get('memory_type', '*')

            # Generate the pattern for sorted set keys
            sorted_set_pattern = f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:messages"

            # Find all matching sorted set keys
            cursor = 0
            sorted_set_keys = []
            while True:
                cursor, keys = connection.connection.scan(cursor=cursor, match=sorted_set_pattern)
                sorted_set_keys.extend(keys)
                if cursor == 0:
                    break

            # Collect all keys and their timestamps from the sorted sets
            all_keys_with_scores = []
            for sorted_set_key in sorted_set_keys:
                keys_with_scores = connection.connection.zrevrange(sorted_set_key, 0, -1, withscores=True)
                all_keys_with_scores.extend(keys_with_scores)

            # Sort all keys globally by timestamp (score) in descending order
            all_keys_with_scores.sort(key=lambda x: x[1], reverse=True)

            # Get the latest `n` keys
            latest_keys = [key_score[0] for key_score in all_keys_with_scores[:n]]

            # Fetch the corresponding values for the latest keys
            results = {}
            for key in latest_keys:
                value = connection.connection.get(key)
                if value:
                    results[key.decode('utf-8')] = eval(value)

            return results if results else f"No messages found for the given context."

        else:
            context_id = memory_context.get('context_id', '*')
            context_entity_id = memory_context.get('context_entity_id', "*")
            memory_type = str(memory_context.get('memory_type', "*"))
            memory_id = memory_context.get('memory_id', "*")

            if memory_type != "*":
                self.validate_memory_type(memory_type)

            pattern = f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:{memory_id}"

            cursor = 0
            matching_keys = []
            while True:
                cursor, keys = connection.connection.scan(cursor=cursor, match=pattern)
                matching_keys.extend(keys)
                if cursor == 0:
                    break

            results = {}
            for key in matching_keys:
                key_type = connection.connection.type(key).decode('utf-8')
                if key_type != 'string':
                    continue
                try:
                    value = connection.connection.get(key)
                    if value:
                        results[key.decode('utf-8')] = eval(value)
                except redis.exceptions.ResponseError as e:
                    print(f"Error reading key {key.decode('utf-8')}: {e}")

            return results if results else f"No matching keys found for pattern '{pattern}'."


    def short_memory_update_quality(self, user_uuid, memory_context, new_memory_type):
        new_memory_type = str(new_memory_type)
        self.validate_memory_type(new_memory_type)

        old_memory_type = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(old_memory_type)

        old_key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            old_memory_type,
            memory_context['memory_id']
        )

        new_key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            new_memory_type,
            memory_context['memory_id']
        )

        connection = self.connections.get("redis_connection")
        if not connection:
            raise ConnectionError("Redis connection is not available.")

        old_value = connection.get(old_key)
        if not old_value:
            return f"Memory '{old_key}' not found."

        memory_data = eval(old_value)
        ttl = memory_data.get('cache_ttl', 3600)
        connection.set(new_key, str(memory_data), ttl)

        redis_client = connection.connection
        redis_client.delete(old_key)

        return f"Memory quality updated to '{new_memory_type}' and key migrated from '{old_key}' to '{new_key}'."

    def short_memory_update_value(self, user_uuid, memory_context, memory):
        """Updates specific fields of a key-value pair in Redis."""
        connection = self.connections.get("redis_connection")
        if not connection:
            raise ConnectionError("Redis connection is not available.")

        memory_type = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(memory_type)

        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            memory_type,
            memory_context['memory_id']
        )

        current_value = connection.get(key)
        if not current_value:
            return f"Key '{key}' not found. Unable to update."

        current_memory = eval(current_value)

        updated_memory = {
            "query_text": memory.get("query_text", current_memory.get("query_text")),
            "response_text": memory.get("response_text", current_memory.get("response_text")),
            "memory_metadata": memory.get("memory_metadata", current_memory.get("memory_metadata")),
            "intent": memory.get("intent", current_memory.get("intent")),
            "entities": memory.get("entities", current_memory.get("entities")),
            "metadata": memory.get("metadata", current_memory.get("metadata")),
        }

        ttl = memory.get('cache_ttl', 3600)
        connection.set(key, str(updated_memory), ttl)

        return f"Key '{key}' updated successfully with value '{updated_memory}' and TTL {ttl}s."