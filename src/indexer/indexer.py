import logging
from apibara.indexer import IndexerRunner, IndexerRunnerConfiguration, Info
from apibara.indexer.indexer import IndexerConfiguration
from apibara.protocol.proto.stream_pb2 import Cursor, DataFinality
from apibara.starknet import EventFilter, Filter, StarkNetIndexer, felt, StateUpdateFilter
from apibara.starknet.cursor import starknet_cursor
from apibara.starknet.proto.starknet_pb2 import Block


root_logger = logging.getLogger("apibara")
# change to `logging.DEBUG` to print more information
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())

factory_address = felt.from_hex(
    "0x0603c4273d547ecfccc3c89bcfce9a11b454e0acb9a1c22166846cfda1ad7756"
)

# `Transfer` selector.
# You can get this value either with starknet.py's `ContractFunction.get_selector`
# or from starkscan.
owner_transfer_key = felt.from_hex(
    "0x1390fd803c110ac71730ece1decfc34eb1d0088e295d4f1b125dda1e0c5b9ff"
)

# `Organization Created Event` selector.

organization_created_key = felt.from_hex(
    "0x2dd16a4a85d0a267447285a74e86fb100b38f5ab580327b76ca744af64b49cc"
)

# # `Creation Fee Event` selector.

creation_fee_updated_key = felt.from_hex(
    "0x3f5dbcd9a0c9c0b4243b796e189e36eec0a4668b352af084dbad3843e86cbd8"
)


guild_created_event_key = felt.from_hex(
    "0x353637d856c66bbee03bf0e7434aba4229169a6e77ba4a86ef93e9ec9781a48"
)

def hex_to_readable_string(hex_string):
    hex_string = hex_string[2:] if hex_string.startswith("0x") else hex_string
    
    byte_string = bytes.fromhex(hex_string)
    
    decoded_string = byte_string.decode('utf-8')
    
    return decoded_string.lstrip('\x00')

class CPIndexer(StarkNetIndexer):
    def indexer_id(self) -> str:
        return "cp-indexer"

    def initial_configuration(self) -> Filter:
        return IndexerConfiguration(
            filter=Filter().add_event(
                EventFilter().with_from_address(factory_address),
                StateUpdateFilter().add_deployed_contract(factory_address)
            ),
            starting_cursor=starknet_cursor(10_000),
            finality=DataFinality.DATA_STATUS_ACCEPTED,
        )
        
    def add_org_address_to_index(self, address) -> Filter:
        print("Organization Added to index")
        return IndexerConfiguration(
            filter=Filter().add_event(
                StateUpdateFilter().add_deployed_contract(felt.from_hex(address))
            ),
            starting_cursor=starknet_cursor(10_000),
            finality=DataFinality.DATA_STATUS_ACCEPTED,
        )

    async def handle_data(self, info: Info, data: Block):
        for event_with_tx in data.events:
            event = event_with_tx.event
            
           
            tx_hash = felt.to_hex(event_with_tx.transaction.meta.hash)
            print("Event")
            print(f"   Tx Hash: {tx_hash}")
           
            if event.keys[0] == owner_transfer_key:
                self._handle_owner_transfer_event(event, tx_hash)
            elif event.keys[0] == organization_created_key:
                self._handle_organization_created_event(event, tx_hash)
            elif event.keys[0] == creation_fee_updated_key:
                self._handle_creation_fee_updated_event(event, tx_hash)
            elif event.keys[0] == guild_created_event_key:
                self._handle_guild_created_event(event, tx_hash)
            else:
                print(f"Unhandled event key: {event.key}")
        

    def _handle_owner_transfer_event(self, event, tx_hash):
        print("Owner Transfer Event")
        print(f"   Tx Hash: {tx_hash}")
        print()

    def _handle_organization_created_event(self, event, tx_hash):
        print("Organization Created Event")
        print(f"   Tx Hash: {tx_hash}")
        name = hex_to_readable_string(felt.to_hex(event.data[0]))
        organization = felt.to_hex(event.data[1])
        self.add_org_address_to_index(organization)
        metadata = felt.to_hex(event.data[2])
        id = felt.to_hex(event.data[3])
        print(f"   Name: {name}")
        print(f"   Organization: {organization}") # Add organization to DB, Index this contract too to track for Guild created events
        print(f"   Metadata: {metadata}")
        print(f"   ID: {id}")
        print()

        # Get sender address and timestamp from tx hash

    def _handle_guild_created_event(self, event, tx_hash):
            print("Guild Created Event")
            print(f"   Tx Hash: {tx_hash}")
            name = hex_to_readable_string(felt.to_hex(event.data[0]))
            id = felt.to_hex(event.data[1])
            guild_address = felt.to_hex(event.data[2])
            print(f"   Name: {name}")
            print(f"   ID: {id}") # Add organization to DB, Index this contract too to track for Guild created events
            print(f"   Guild Address: {guild_address}")
            print(f"   ID: {id}")
            print()

    def _handle_creation_fee_updated_event(self, event, tx_hash):
        print("Creation Fee Updated Event")
        print(f"   Tx Hash: {tx_hash}")
        new_fee = felt.to_hex(event.data[0])
        print(f'new fee is' + new_fee)
        print()

    async def handle_invalidate(self, _info: Info, _cursor: Cursor):
        raise ValueError("data must be finalized")



async def run_indexer(server_url=None, mongo_url=None, restart=None, dna_token=None):
    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            stream_url=server_url,
            storage_url=mongo_url,
            token=dna_token,
            

        ),
        reset_state=restart,
        
    
        
    )


    # ctx can be accessed by the callbacks in `info`.
    await runner.run(CPIndexer(), ctx={"network": "starknet-sepolia"})
