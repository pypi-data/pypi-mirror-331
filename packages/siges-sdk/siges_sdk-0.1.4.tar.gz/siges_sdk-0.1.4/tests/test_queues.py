import pytest
import redis
from unittest.mock import MagicMock, patch
import asyncio
from siges_sdk.queues import (
    QueueMessageProducer,
    QueueMessageConsumer,
    get_message_producer
)
from siges_sdk.queues.redis_message_producer import RedisMessageProducer
from siges_sdk.queues.redis_message_consumer import RedisQueueMessageConsumer

@patch('redis.Redis')
def test_redis_message_consumer_with_max_length(mock_redis):
    """Test que verifica la configuración de max_stream_length en el consumidor Redis"""
    # Configurar el mock
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    async def callback(message):
        return True
    
    # Crear el consumidor con max_stream_length
    queue_name = "test-queue"
    consumer_group = "test-group"
    max_length = 1000
    
    consumer = RedisQueueMessageConsumer(
        queue_name=queue_name,
        callback=callback,
        consumer_group=consumer_group,
        max_stream_length=max_length
    )
    
    # Verificar que se llamó a xadd para configurar el max_length
    mock_redis_instance.xadd.assert_called_once_with(
        queue_name,
        {'dummy': 'dummy'},
        maxlen=max_length,
        approximate=True
    )
    
    # Verificar que se eliminó el mensaje dummy
    mock_redis_instance.xdel.assert_called_once_with(queue_name, '0-0')

@patch('redis.Redis')
def test_redis_message_consumer_process_message(mock_redis):
    """Test que verifica el procesamiento de mensajes en el consumidor Redis"""
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Simular mensajes en la cola
    mock_redis_instance.xreadgroup.return_value = [
        [b'test-queue', [(b'1234-0', {b'key': b'value'})]]
    ]
    
    processed_messages = []
    async def callback(message):
        processed_messages.append(message)
    
    consumer = RedisQueueMessageConsumer(
        queue_name="test-queue",
        callback=callback,
        consumer_group="test-group"
    )
    
    # Iniciar y detener rápidamente para procesar un mensaje
    consumer.start()
    # Esperar un momento para que se procese el mensaje
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
    consumer.stop()
    
    # Verificar que se procesó el mensaje
    assert len(processed_messages) == 1
    assert b'key' in processed_messages[0]
    
    # Verificar que se confirmó el mensaje
    mock_redis_instance.xack.assert_called_with(
        "test-queue",
        "test-group",
        b'1234-0'
    )

@patch('redis.Redis')
def test_redis_message_consumer_error_handling(mock_redis):
    """Test que verifica el manejo de errores en el consumidor Redis"""
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance
    
    # Simular un error en xreadgroup
    mock_redis_instance.xreadgroup.side_effect = redis.RedisError("Test error")
    
    async def callback(message):
        return True
    
    consumer = RedisQueueMessageConsumer(
        queue_name="test-queue",
        callback=callback,
        consumer_group="test-group"
    )
    
    # El consumidor debería manejar el error sin fallar
    consumer.start()
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
    consumer.stop()
    
    # Verificar que se intentó leer mensajes
    assert mock_redis_instance.xreadgroup.called 