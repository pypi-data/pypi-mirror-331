from typing import List, Optional
from pydantic import BaseModel, Field

from onilock.core.logging_manager import logger
from onilock.core.utils import naive_utcnow


# @TODO : Rename to Account
class Account(BaseModel):
    id: str = Field(description="Password Identification")
    username: str = Field(default="", description="Username")
    encrypted_password: str = Field(description="Encrypted Password")
    url: Optional[str] = Field(default=None, description="URL or Service name")
    description: Optional[str] = Field(default=None, description="Description")
    created_at: int = Field(description="Creation date")


class Profile(BaseModel):
    name: str
    master_password: str = Field(description="Hashed Master Password")
    vault_version: str = Field(default="", description="Vault version")
    creation_timestamp: float = Field(
        default=naive_utcnow().timestamp(), description="Creation time"
    )
    accounts: List[Account]

    def get_account(self, id: str | int) -> Account | None:
        if isinstance(id, int):
            try:
                return self.accounts[id]
            except IndexError:
                logger.error("Invalid account index")
                return None

        for account in self.accounts:
            if account.id.lower() == id.lower():
                return account
        return None

    def remove_account(self, id: str):
        for index, password in enumerate(self.accounts):
            if password.id.lower() == id.lower():
                del self.accounts[index]
                break
