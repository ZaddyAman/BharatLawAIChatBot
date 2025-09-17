"""
Dependency Injection Container
Replaces global singletons with proper dependency injection
"""

from typing import Optional
from rag.advanced_rag import AdvancedRAGSystem
from services.scalable_registry import ScalableRegistry
from config import AppConfig


class DependencyContainer:
    """
    Dependency injection container for managing service instances
    """

    def __init__(self, config: AppConfig):
        self._config = config
        self._rag_system: Optional[AdvancedRAGSystem] = None
        self._registry: Optional[ScalableRegistry] = None

    def get_rag_system(self) -> AdvancedRAGSystem:
        """Get or create RAG system instance"""
        if self._rag_system is None:
            self._rag_system = AdvancedRAGSystem()
        return self._rag_system

    def get_registry(self) -> ScalableRegistry:
        """Get or create registry instance"""
        if self._registry is None:
            self._registry = ScalableRegistry()
        return self._registry

    def reset(self):
        """Reset all instances (useful for testing)"""
        self._rag_system = None
        self._registry = None


# Global container instance
_container: Optional[DependencyContainer] = None


def init_container(config: AppConfig) -> DependencyContainer:
    """Initialize the global dependency container"""
    global _container
    _container = DependencyContainer(config)
    return _container


def get_container() -> DependencyContainer:
    """Get the global dependency container"""
    if _container is None:
        raise RuntimeError("Dependency container not initialized. Call init_container() first.")
    return _container


def get_rag_system() -> AdvancedRAGSystem:
    """Convenience function to get RAG system"""
    return get_container().get_rag_system()


def get_registry() -> ScalableRegistry:
    """Convenience function to get registry"""
    return get_container().get_registry()