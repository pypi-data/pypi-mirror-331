from typing import Union
from pydantic import BaseModel
from fastapi import APIRouter

from .Users import router as users_router
from .Conversations import router as conversations_router
from .Comments import router as comments_router
from .utils import DEFAULT_CONFIG, connect_db

router = APIRouter(tags=["Database"])
package_name = __name__.split('.')[-2]
prefix = '_'.join(package_name.split('_')[2:])
dependencies = []

def init(config=None):
    """Initialize the router with the given configuration.

    Args:
        config: A configparser.ConfigParser object containing the configuration.

    Returns:
        The initialized APIRouter object.
    """
    if config:
        for k in DEFAULT_CONFIG.keys():
            config.get(package_name, k)
    connect_db()
    router = APIRouter(tags=["Database"])
    router.include_router(users_router)
    router.include_router(conversations_router)
    router.include_router(comments_router)
    return router
