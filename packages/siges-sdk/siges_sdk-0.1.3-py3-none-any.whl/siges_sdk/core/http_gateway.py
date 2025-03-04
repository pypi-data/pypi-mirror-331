import httpx
from .gateway import CoreGateway, PluginRegisterRequest
import logging

logger = logging.getLogger(__name__)

class HttpCoreGateway(CoreGateway):
    """
    Implementación HTTP del gateway para comunicarse con el core.
    """
    def __init__(self, core_url: str = "http://siges-core:8000"):
        self.core_url = core_url
    
    async def register_plugin(self, plugin_register_request: PluginRegisterRequest) -> None:
        """
        Registra un plugin en el core mediante una solicitud HTTP.
        
        Args:
            plugin_register_request: Solicitud de registro del plugin
        
        Raises:
            Exception: Si ocurre un error al registrar el plugin
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.core_url}/plugin/register", 
                    json=plugin_register_request.to_dict(),
                    timeout=10.0
                )
                if response.status_code != 200:
                    raise Exception(f"Error al registrar plugin: {response.json()}")
                logger.info(f"Plugin {plugin_register_request.name} registrado correctamente")
            except httpx.RequestError as e:
                logger.error(f"Error de conexión al registrar plugin: {e}")
                raise Exception(f"Error de conexión al registrar plugin: {e}")
