import logging

from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.transaction import submit_and_wait
from xrpl.models.transactions.transaction import Transaction as XrplTransaction
from xrpl.wallet import Wallet

from postfiat.models.transaction import Transaction
from postfiat.rpc.errors import RpcSendError

log = logging.getLogger(__name__)


class RpcSender():

    def __init__(self, endpoint: str):
        self.xrpl_client = AsyncJsonRpcClient(endpoint)

    async def submit_and_wait(self, txn: Transaction, wallet: Wallet) -> list[str]:
        try:
            return await submit_and_wait(
                XrplTransaction.from_dict(txn.to_dict()),
                self.xrpl_client,
                wallet,
            )
        except Exception as e:
            log.error(f"Failed to send transaction: {txn} from wallet: {wallet}")
            raise RpcSendError(f"Failed to send transaction: {e}") from e
