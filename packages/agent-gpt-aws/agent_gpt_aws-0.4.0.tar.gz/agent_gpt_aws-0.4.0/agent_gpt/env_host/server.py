from threading import Thread, Event
from .env_api import EnvAPI

class EnvServer(EnvAPI):
    """
    EnvServer extends EnvAPI to manage environment hosting locally.
    It integrates the launching functionality so that you can simply call
    EnvServer.launch(...) to start a server.
    """
    def __init__(self, env_type="gym", host="0.0.0.0", port=8000):

        if env_type.lower() == "gym":
            from ..wrappers.gym_env import GymEnv
            env_wrapper = GymEnv
            # print("[server.py] Using GymEnv wrapper.")
                   
        elif env_type.lower() == "unity":
            try:
                import mlagents_envs
                import google.protobuf
            except ImportError as e:
                raise ImportError("Required packages for Unity environment are missing: " + str(e))
            
            # Check for required versions. Allow minor patch differences if desired.
            if not mlagents_envs.__version__.startswith("0.30"):
                raise ImportError(f"mlagents_envs version 0.30 is required, but found {mlagents_envs.__version__}")
            if not google.protobuf.__version__.startswith("3.20"):
                raise ImportError(f"protobuf version 3.20 is required, but found {google.protobuf.__version__}")
            
            from ..wrappers.unity_env import UnityEnv
            env_wrapper = UnityEnv
            # print("[server.py] Using UnityEnv wrapper.")

        else:
            raise ValueError(f"Unknown env type '{env_type}'. Choose 'unity' or 'gym'.")


        # Optionally call the parent's initializer
        super().__init__(env_wrapper, host, port)

        self.api = EnvAPI(env_wrapper=env_wrapper, host=host, port=port)
                
        self.endpoint = None
        self.url = None
        self.host = host
        self.port = port

        # Create a shutdown event that can be used for graceful termination.
        self.shutdown_event = Event()

    def run_thread_server(self):
        """Run the server in a separate daemon thread with a graceful shutdown mechanism."""
        self.server_thread = Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        return self.server_thread

    def shutdown(self):
        """Signal the server to shut down gracefully."""
        self.shutdown_event.set()
        # Additional logic would be needed here to stop the uvicorn server, etc.

    @classmethod
    def launch(cls, env_type: str, url: str, host: str = "0.0.0.0", port: int = 8000) -> "EnvServer":
        """
        Create an EnvServer instance, launch its server in a separate thread,
        and set the public URL (defaulting to http://host:port).
        """
        instance = cls(env_type, host, port)
        instance.run_thread_server()
        # Default ip to host if not provided
        # print(f"[AgentGPTTrainer] Launching environment at {url}:{port}")
        instance.url = url
        instance.port = port
        instance.endpoint = f"{url}:{port}"
        return instance
